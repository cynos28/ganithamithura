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

# Import BOTH tutors
# NOTE: User specified 'voice_ai_math_tuor.py' (sic)
from src.components.voice_ai_math_tuor import SimpleVoiceMathTutor
from src.components.ai_math_tutor import AIMathTutor
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SymbolTutorServer")

load_dotenv()

app = FastAPI()

# --- VOICE WRAPPER ---
class WebSocketVoiceWrapper(SimpleVoiceMathTutor):
    """
    Wraps SimpleVoiceMathTutor (User specified) for Websocket (VOICE MODE)
    Overrides speak() and listen_for_answer() to use WebSocket.
    """
    def __init__(self, websocket: WebSocket, grade: int, level: int, sublevel: str):
        super().__init__(grade=grade, level=level, sublevel=sublevel)
        self.websocket = websocket
        self.input_queue = Queue()
        self.main_loop = None

    def speak(self, text: str):
        """Override speak to send 'speak' message to frontend for TTS"""
        print(f"Voice Server Speaking: {text}") 
        try:
            if self.main_loop:
                asyncio.run_coroutine_threadsafe(
                    self.websocket.send_json({"type": "speak", "text": text}), 
                    self.main_loop
                ).result()
        except Exception as e:
            logger.error(f"Error sending speak: {e}")
            
        # Simulate speech duration for synchronization
        # SimpleVoiceMathTutor doesn't wait automatically in 'speak' usually, 
        # but we add delays here to prevent rushing.
        time.sleep(len(text) * 0.08 + 0.5)

    def listen_for_answer(self, timeout: int = None) -> str:
        """Override to wait for frontend input via WebSocket instead of microphone"""
        # Signal frontend to listen? (It handles auto-listening usually)
        try:
            logger.info("Waiting for user voice input...")
            # Blocking wait for input from queue
            user_input = self.input_queue.get(timeout=300) 
            logger.info(f"Received voice input: {user_input}")
            return str(user_input)
        except Exception:
            return None

    def ask_question(self, question_data: dict) -> bool:
        """
        Override ask_question to inject Visual WebSocket messages 
        BEFORE letting the Base Logic handle the Voice/Interaction flow.
        """
        # 1. Send Expression (Visual)
        if 'expression' in question_data:
             expression_text = f"{question_data['expression']} = ?"
             try:
                 if self.main_loop:
                     asyncio.run_coroutine_threadsafe(
                        self.websocket.send_json({"type": "expression", "text": expression_text}), 
                        self.main_loop
                    ).result()
             except Exception: pass

        # 2. Send Image (if available)
        if 'image_url' in question_data and question_data['image_url']:
             try:
                if self.main_loop:
                     asyncio.run_coroutine_threadsafe(
                        self.websocket.send_json({"type": "image", "url": question_data['image_url']}), 
                        self.main_loop
                    ).result()
             except Exception: pass

        # 3. Delegate to Original Logic for Voice Interaction
        result = super().ask_question(question_data)

        # 4. Send Feedback Signal for Frontend Counter
        # The SimpleVoiceMathTutor already spoke the logic feedback ("Excellent", etc.) via speak().
        # We send this message primarily to trigger the frontend counter increment.
        try:
            if self.main_loop:
                 asyncio.run_coroutine_threadsafe(
                    self.websocket.send_json({
                        "type": "feedback", 
                        "text": "Correct!" if result is True else "Practice makes perfect!",
                        "isCorrect": result is True
                    }), 
                    self.main_loop
                ).result()
        except Exception: pass

        return result
    
    def set_loop(self, loop):
        self.main_loop = loop
    
    # We use the Base class 'run_session' which calls 'ask_question' (our override), 
    # effectively running the USER'S logic loop but with redirected I/O and added visuals.



# --- TEXT WRAPPER ---
class WebSocketTextWrapper(AIMathTutor):
    """
    Wraps AIMathTutor for Websocket (TEXT MODE)
    """
    def __init__(self, websocket: WebSocket, grade: int, level: int, sublevel: str):
        super().__init__(grade=grade, performance_level=level, sublevel=sublevel)
        self.websocket = websocket
        self.input_queue = Queue()
        self.main_loop = None

    def speak_with_display(self, text: str):
        """Send text to frontend (No TTS implied)"""
        print(f"Text Server message: {text}") 
        try:
            if self.main_loop:
                asyncio.run_coroutine_threadsafe(
                    # Use 'speak' type so frontend handles it effectively as a message bubble
                    # but implementation implies Reading not Listening
                    self.websocket.send_json({"type": "speak", "text": text}), 
                    self.main_loop
                ).result()
        except Exception as e:
            logger.error(f"Error sending text: {e}")

    def _display_image(self, image_url: str):
        """Send image URL"""
        try:
            if self.main_loop:
                 asyncio.run_coroutine_threadsafe(
                    self.websocket.send_json({"type": "image", "url": image_url}), 
                    self.main_loop
                ).result()
        except: pass

    def send_feedback(self, text: str, is_correct: bool):
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
        except: pass
        
        # Text Mode: Fast feedback, minimal delay
        time.sleep(2.0) 

    def ask_question(self, question_data):
        """Ask question flow for TEXT"""
        # 1. Send Image
        if self.enable_images and 'image_url' in question_data:
            self._display_image(question_data['image_url'])

        # 2. Send Expression
        expression_text = f"{question_data['expression']} = ?"
        try:
             if self.main_loop:
                 asyncio.run_coroutine_threadsafe(
                    self.websocket.send_json({"type": "expression", "text": expression_text}), 
                    self.main_loop
                ).result()
        except: pass

        # 3. Show Question Text
        self.speak_with_display(question_data['question_text'])
        # No sleep needed for reading time in async flow, user reads at own pace

        # 4. Get Input
        user_input = self.get_user_input()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            return 'quit'

        # 5. Check Answer
        try:
            user_answer = float(user_input)
        except ValueError:
            self.speak_with_display("Please enter a number.")
            return False

        correct_answer = float(question_data['answer'])
        is_correct = (abs(user_answer - correct_answer) < 0.01)

        if is_correct:
            # Simple feedback for text mode
            self.send_feedback("Correct!", True)
            return True
        else:
            self.send_feedback(f"Wrong. Answer is {correct_answer}.", False)
            return False

    def get_user_input(self) -> str:
        try:
            return str(self.input_queue.get(timeout=300))
        except:
            return "quit"

    def set_loop(self, loop):
        self.main_loop = loop


# Global Cache
# tutors_cache = {}  # Removed to prevent zombie processes

# Removed warmup_tutor endpoint to stop runaway generation

# --- ENDPOINT 1: TEXT TUTOR (Typing) ---
@app.websocket("/ws/tutor/{grade}/{level}/{sublevel}")
async def websocket_tutor_text(websocket: WebSocket, grade: int, level: int, sublevel: str):
    await websocket.accept()
    logger.info(f"TEXT Client connected: Grade {grade}, Level {level}")
    
    # Initialize Text Wrapper
    agent = WebSocketTextWrapper(websocket, grade, level, sublevel)
    
    # Start generation (Text Tutor still uses queue, that's fine as it's active session)
    agent.start_queue_worker()

    agent.set_loop(asyncio.get_running_loop())
    
    # Run
    agent_thread = threading.Thread(target=agent.run_session, args=(5,), daemon=True)
    agent_thread.start()

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message.get("type") == "input":
                agent.input_queue.put(message.get("value"))
    except WebSocketDisconnect:
        logger.info("Client disconnected")
        agent.stop_queue_worker()
    except Exception as e:
        logger.error(f"Error handling websocket: {e}")


# --- ENDPOINT 2: VOICE TUTOR (Telling) ---
@app.websocket("/ws/voice-tutor/{grade}/{level}/{sublevel}")
async def websocket_tutor_voice(websocket: WebSocket, grade: int, level: int, sublevel: str):
    await websocket.accept()
    logger.info(f"VOICE Client connected: Grade {grade}, Level {level}")
    
    # Initialize Voice Wrapper (SimpleVoiceMathTutor)
    agent = WebSocketVoiceWrapper(websocket, grade, level, sublevel)
    
    # No queue worker to start for SimpleVoiceMathTutor - it generates on-demand

    agent.set_loop(asyncio.get_running_loop())
    
    # Run
    agent_thread = threading.Thread(target=agent.run_session, args=(5,), daemon=True)
    agent_thread.start()

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message.get("type") == "input":
                agent.input_queue.put(message.get("value"))
    except WebSocketDisconnect:
        logger.info("Client disconnected")
        # No queue worker to stop
    except Exception as e:
        logger.error(f"Error handling websocket: {e}")
