import os
import sys
import asyncio
import json
import threading
import logging
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from queue import Queue
from pydantic import BaseModel

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import the Question Answering Agent instead of LearningCurveAgent
from src.components.ai_math_tutor_voice import AIVoiceMathTutor
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SymbolTutorServer")

load_dotenv()

app = FastAPI()

class WebSocketQuestionWrapper(AIVoiceMathTutor):
    """
    Wraps AIVoiceMathTutor to communicate via WebSocket.
    Overrides I/O methods to use WebSocket messages.
    """
    def __init__(self, websocket: WebSocket, grade: int, level: int, sublevel: str):
        # Initialize parent with config
        super().__init__(grade=grade, performance_level=level, sublevel=sublevel)
        
        self.websocket = websocket
        self.input_queue = Queue()
        self.main_loop = None # Will be set later

    def speak_with_display(self, text: str):
        """Override speak to send text to frontend via WebSocket"""
        print(f"Server Speaking: {text}") 
        try:
            if self.main_loop:
                asyncio.run_coroutine_threadsafe(
                    self.websocket.send_json({"type": "speak", "text": text}), 
                    self.main_loop
                ).result()
        except Exception as e:
            logger.error(f"Error sending speak: {e}")

    def _display_image(self, image_url: str):
        """Override to send image URL to frontend"""
        print(f"Server Sending Image: {image_url}")
        try:
            if self.main_loop:
                 asyncio.run_coroutine_threadsafe(
                    self.websocket.send_json({"type": "image", "url": image_url}), 
                    self.main_loop
                ).result()
        except Exception as e:
            logger.error(f"Error sending image: {e}")

    def send_feedback(self, text: str, is_correct: bool):
        """Send feedback message and simulate speech duration"""
        print(f"Server Sending Feedback: {text}")
        try:
            if self.main_loop:
                 asyncio.run_coroutine_threadsafe(
                    self.websocket.send_json({
                        "type": "feedback", 
                        "text": text,
                        "isCorrect": is_correct
                    }), 
                    self.main_loop
                ).result()
        except Exception as e:
            logger.error(f"Error sending feedback: {e}")
        
        # VALIDATION FIX: Block backend to prevent racing to next question
        # Simulate speech time: ~0.08s per character
        sleep_time = len(text) * 0.08
        time.sleep(sleep_time + 1.0) # Add 1s buffer

    def ask_question(self, question_data):
        """
        Fully overridden ask_question to control the flow and message types.
        """
        # 1. Send Image
        if self.enable_images and 'image_url' in question_data and question_data['image_url']:
            self._display_image(question_data['image_url'])

        # 2. Send Expression
        expression_text = f"{question_data['expression']} = ?"
        try:
             if self.main_loop:
                 asyncio.run_coroutine_threadsafe(
                    self.websocket.send_json({"type": "expression", "text": expression_text}), 
                    self.main_loop
                ).result()
        except Exception as e:
            logger.error(f"Error sending expression: {e}")

        # 3. Speak Question
        self.speak_with_display(question_data['question_text'])
        # Block slightly for question speech
        time.sleep(len(question_data['question_text']) * 0.08)

        # 4. Get Input
        user_input = self.get_user_input() # This blocks waiting for WebSocket message
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            return 'quit'

        # 5. Check Answer
        try:
            user_answer = float(user_input) # Support float answers
        except ValueError:
            self.speak_with_display("Please enter a number.")
            return False

        correct_answer = float(question_data['answer'])
        is_correct = (abs(user_answer - correct_answer) < 0.01)

        if is_correct:
            response = self._generate_correct_feedback(correct_answer, question_data['question_text'])
            self.send_feedback(response, True)
            return True
        else:
            response = self._generate_wrong_feedback(
                user_answer, 
                correct_answer, 
                question_data['question_text'], 
                question_data['expression']
            )
            self.send_feedback(response, False)
            return False

    def get_user_input(self) -> str:
        """Override to wait for frontend input via WebSocket"""
        # Signal frontend to show input if needed (optional, or just wait)
        # self.speak_with_display("Waiting for input...")
        
        try:
            logger.info("Waiting for user input...")
            # Blocking wait for input from queue
            user_input = self.input_queue.get(timeout=300) # 5 min timeout
            logger.info(f"Received input: {user_input}")
            return str(user_input)
        except Exception:
            return "quit"

    def set_loop(self, loop):
        self.main_loop = loop

# Global Cache for Reuse
tutors_cache = {}

class TutorRequest(BaseModel):
    grade: int
    level: int
    sublevel: str

@app.post("/warmup-tutor/{grade}/{level}/{sublevel}")
async def warmup_tutor(grade: int, level: int, sublevel: str):
    """Start generating questions before the user connects via WebSocket"""
    key = f"{grade}-{level}-{sublevel}"
    print(f"Warmup requested for: {key}")
    
    if key not in tutors_cache:
        # Create a standard tutor to start generating
        # Mimic Wrapper Init: passes 'level' as 'performance_level'
        tutor = AIVoiceMathTutor(grade=grade, performance_level=level, sublevel=sublevel) 
        tutor.start_queue_worker() # Start generating!
        tutors_cache[key] = tutor
        print(f"Started Checked/Cached Tutor for {key}")
    else:
        print(f"Tutor already warm for {key}")
    
    return {"status": "warming_up", "queue_size": tutors_cache[key].question_queue.qsize()}

@app.websocket("/ws/tutor/{grade}/{level}/{sublevel}")
async def websocket_endpoint(websocket: WebSocket, grade: int, level: int, sublevel: str):
    await websocket.accept()
    logger.info(f"Client connected: Grade {grade}, Level {level}, Phase {sublevel}")
    
    key = f"{grade}-{level}-{sublevel}"
    
    # Check if we have a warm tutor
    cached_queue = None
    if key in tutors_cache:
        print(f"Found warm tutor for {key}. Using pre-generated queue.")
        cached_tutor = tutors_cache[key]
        cached_queue = cached_tutor.question_queue

    # Initialize Question Wrapper (AIVoiceMathTutor)
    agent = WebSocketQuestionWrapper(websocket, grade, level, sublevel)
    
    if cached_queue:
        # INJECT THE WARM QUEUE
        agent.question_queue = cached_queue
        # Note: The cached_tutor's worker thread is still running and filling this queue.
        # This is perfect.

    agent.set_loop(asyncio.get_running_loop())

    # Run agent in a separate thread because it's blocking
    agent_thread = threading.Thread(target=agent.run_session, args=(10,), daemon=True) # 10 questions default
    agent_thread.start()

    try:
        while True:
            # Listen for messages from Frontend
            data = await websocket.receive_json()
            logger.info(f"Received message: {data}")
            
            if data.get("type") == "input":
                # Push input to the queue
                agent.input_queue.put(data.get("value"))
            
            elif data.get("type") == "stop":
                 break

    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"Error handling websocket: {e}")
