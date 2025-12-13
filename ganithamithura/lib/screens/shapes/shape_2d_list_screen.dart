import 'package:flutter/material.dart';
import 'package:ganithamithura/models/shape_2d_model.dart';

class Shape2DListScreen extends StatelessWidget {
  const Shape2DListScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final List<Shape2D> shapes = [
      Shape2D(
        name: 'Circle',
        description: 'A circle is a shape consisting of all points in a plane that are at a given distance from a given point, the centre.',
        image: 'assets/images/shapes/circle.png',
      ),
      Shape2D(
        name: 'Square',
        description: 'A square is a regular quadrilateral, which means that it has four equal sides and four equal angles (90-degree angles, or right angles).',
        image: 'assets/images/shapes/square.png',
      ),
      Shape2D(
        name: 'Rectangle',
        description: 'A rectangle is a quadrilateral with four right angles. It can also be defined as an equiangular quadrilateral, since equiangular means that all of its angles are equal.',
        image: 'assets/images/shapes/rectangle.png',
      ),
      Shape2D(
        name: 'Triangle',
        description: 'A triangle is a polygon with three edges and three vertices. It is one of the basic shapes in geometry.',
        image: 'assets/images/shapes/triangle.png',
      ),
    ];

    return Scaffold(
      appBar: AppBar(
        title: const Text('2D Shapes'),
      ),
      body: ListView.builder(
        itemCount: shapes.length,
        itemBuilder: (context, index) {
          final shape = shapes[index];
          return Card(
            margin: const EdgeInsets.all(10),
            child: Padding(
              padding: const EdgeInsets.all(10),
              child: Column(
                children: [
                  Image.asset(
                    shape.image,
                    height: 100,
                    width: 100,
                    fit: BoxFit.contain,
                  ),
                  const SizedBox(height: 10),
                  Text(
                    shape.name,
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 5),
                  Text(
                    shape.description,
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
