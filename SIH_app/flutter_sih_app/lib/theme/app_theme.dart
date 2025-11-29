import 'package:flutter/material.dart';

// Shared app background gradient (matches the login page)
const LinearGradient kAppBackgroundGradient = LinearGradient(
  begin: Alignment.topLeft,
  end: Alignment.bottomRight,
  colors: [
    Colors.white,
    Color(0xFFe6f4ea), // soft green
    Color(0xFFFFF2DE), // soft orange/cream
    Color(0xFFd6f0d0), // green tint
  ],
);

Decoration get appBackgroundDecoration =>
    const BoxDecoration(gradient: kAppBackgroundGradient);

// Convenience: a plain background color fallback for simpler pages
Color get appBackgroundColor => const Color(0xFFe6f4ea);
