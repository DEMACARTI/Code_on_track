import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import '../services/auth_service.dart';

class LoginPage extends StatefulWidget {
  final AuthService authService;

  const LoginPage({super.key, required this.authService});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage>
    with SingleTickerProviderStateMixin {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;
  bool _obscurePassword = true;
  String? _errorMessage;
  late final AnimationController _animController;
  late final Animation<Offset> _cardOffset;
  late final Animation<double> _logoScale;
  final FocusNode _usernameFocus = FocusNode();
  final FocusNode _passwordFocus = FocusNode();

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    _usernameFocus.dispose();
    _passwordFocus.dispose();
    _animController.dispose();
    super.dispose();
  }

  bool _isFormValid() {
    return _usernameController.text.isNotEmpty &&
        _passwordController.text.isNotEmpty;
  }

  void _handleLogin() async {
    if (_formKey.currentState!.validate()) {
      setState(() {
        _isLoading = true;
        _errorMessage = null;
      });

      final user = await widget.authService.authenticate(
        _usernameController.text.trim(),
        _passwordController.text,
      );

      if (mounted) {
        setState(() => _isLoading = false);

        if (user != null) {
          Navigator.of(
            context,
          ).pushReplacementNamed('/dashboard', arguments: user);
        } else {
          setState(() {
            _errorMessage = 'Invalid username or password';
          });
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Login failed. Please try again.'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    }
  }

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    );

    _cardOffset = Tween<Offset>(
      begin: const Offset(0, 0.25),
      end: Offset.zero,
    ).animate(CurvedAnimation(parent: _animController, curve: Curves.easeOut));
    _logoScale = Tween<double>(begin: 0.7, end: 1.0).animate(
      CurvedAnimation(parent: _animController, curve: Curves.elasticOut),
    );

    // start entrance animation
    _animController.forward();

    // Update UI when focus or content changes so hints can hide/show
    _usernameFocus.addListener(() => setState(() {}));
    _passwordFocus.addListener(() => setState(() {}));
    _usernameController.addListener(() => setState(() {}));
    _passwordController.addListener(() => setState(() {}));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: GestureDetector(
        onTap: () => FocusScope.of(context).unfocus(),
        child: Stack(
          children: [
            // Animated gradient background
            Positioned.fill(
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 800),
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      Colors.white,
                      Color(0xFFe6f4ea), // soft green
                      Color(0xFFFFF2DE), // soft orange/cream
                      Color(0xFFd6f0d0), // green tint
                    ],
                  ),
                ),
              ),
            ),

            // Decorative circles
            Positioned(
              top: -80,
              left: -60,
              child: AnimatedOpacity(
                opacity: 0.9,
                duration: const Duration(milliseconds: 900),
                child: Container(
                  width: 220,
                  height: 220,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: RadialGradient(
                      colors: [
                        Colors.green.withValues(alpha: 0.14),
                        Colors.transparent,
                      ],
                    ),
                  ),
                ),
              ),
            ),

            Positioned(
              bottom: -100,
              right: -80,
              child: AnimatedOpacity(
                opacity: 0.85,
                duration: const Duration(milliseconds: 1000),
                child: Container(
                  width: 280,
                  height: 280,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: RadialGradient(
                      colors: [
                        Colors.orange.withValues(alpha: 0.12),
                        Colors.transparent,
                      ],
                    ),
                  ),
                ),
              ),
            ),

            SafeArea(
              child: Center(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 24.0,
                    vertical: 36,
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      // Animated logo (app image) with safe fallback
                      ScaleTransition(
                        scale: _logoScale,
                        child: SizedBox(
                          width: 200,
                          height: 200,
                          child: Image.asset(
                            'assets/images/SIH_LOGO.png',
                            fit: BoxFit.contain,
                            // If PNG not yet present or fails to load, fall back to the SVG placeholder
                            errorBuilder: (context, error, stackTrace) {
                              return SvgPicture.asset(
                                'assets/images/rail_chinh_logo.svg',
                                fit: BoxFit.contain,
                                semanticsLabel: 'Rail Chinh logo',
                                placeholderBuilder: (context) => Container(
                                  decoration: BoxDecoration(
                                    color: Colors.white,
                                    shape: BoxShape.circle,
                                  ),
                                  child: const Center(
                                    child: Icon(
                                      Icons.train,
                                      size: 36,
                                      color: Colors.green,
                                    ),
                                  ),
                                ),
                              );
                            },
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                      const Text(
                        'SIH Dashboard',
                        style: TextStyle(
                          fontSize: 32,
                          fontWeight: FontWeight.bold,
                          color: Colors.black87,
                        ),
                      ),
                      const SizedBox(height: 6),
                      const Text(
                        'Smart Infrastructure Hub',
                        style: TextStyle(fontSize: 14, color: Colors.black54),
                      ),
                      const SizedBox(height: 28),

                      // Frosted glass card with slide animation
                      SlideTransition(
                        position: _cardOffset,
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(20),
                          child: BackdropFilter(
                            filter: ImageFilter.blur(sigmaX: 8.0, sigmaY: 8.0),
                            child: Container(
                              width: double.infinity,
                              padding: const EdgeInsets.all(22),
                              decoration: BoxDecoration(
                                color: Colors.white.withValues(alpha: 0.75),
                                borderRadius: BorderRadius.circular(20),
                                boxShadow: [
                                  BoxShadow(
                                    color: Colors.black.withValues(alpha: 0.08),
                                    blurRadius: 18,
                                    offset: const Offset(0, 8),
                                  ),
                                ],
                                border: Border.all(
                                  color: Colors.white.withValues(alpha: 0.6),
                                ),
                              ),
                              child: Form(
                                key: _formKey,
                                child: Column(
                                  crossAxisAlignment:
                                      CrossAxisAlignment.stretch,
                                  children: [
                                    // Username Field
                                    AnimatedContainer(
                                      duration: const Duration(
                                        milliseconds: 300,
                                      ),
                                      decoration: BoxDecoration(
                                        borderRadius: BorderRadius.circular(12),
                                        border: Border.all(
                                          color: _usernameFocus.hasFocus
                                              ? Colors.green.shade700
                                              : Colors.transparent,
                                          width: 2,
                                        ),
                                      ),
                                      padding: const EdgeInsets.all(2),
                                      child: TextFormField(
                                        focusNode: _usernameFocus,
                                        controller: _usernameController,
                                        decoration: InputDecoration(
                                          // show hint only when not focused and empty
                                          hintText:
                                              !_usernameFocus.hasFocus &&
                                                  _usernameController
                                                      .text
                                                      .isEmpty
                                              ? 'Username'
                                              : null,
                                          prefixIcon: const Icon(Icons.person),
                                          filled: true,
                                          fillColor: Colors.white,
                                          border: OutlineInputBorder(
                                            borderRadius: BorderRadius.circular(
                                              12,
                                            ),
                                            borderSide: BorderSide.none,
                                          ),
                                        ),
                                        validator: (value) {
                                          if (value == null || value.isEmpty) {
                                            return 'Please enter username';
                                          }
                                          return null;
                                        },
                                        enabled: !_isLoading,
                                      ),
                                    ),
                                    const SizedBox(height: 14),

                                    // Password Field
                                    AnimatedContainer(
                                      duration: const Duration(
                                        milliseconds: 300,
                                      ),
                                      decoration: BoxDecoration(
                                        borderRadius: BorderRadius.circular(12),
                                        border: Border.all(
                                          color: _passwordFocus.hasFocus
                                              ? Colors.orange.shade700
                                              : Colors.transparent,
                                          width: 2,
                                        ),
                                      ),
                                      padding: const EdgeInsets.all(2),
                                      child: TextFormField(
                                        focusNode: _passwordFocus,
                                        controller: _passwordController,
                                        obscureText: _obscurePassword,
                                        decoration: InputDecoration(
                                          // show hint only when not focused and empty
                                          hintText:
                                              !_passwordFocus.hasFocus &&
                                                  _passwordController
                                                      .text
                                                      .isEmpty
                                              ? 'Password'
                                              : null,
                                          prefixIcon: const Icon(Icons.lock),
                                          suffixIcon: IconButton(
                                            icon: Icon(
                                              _obscurePassword
                                                  ? Icons.visibility_off
                                                  : Icons.visibility,
                                            ),
                                            onPressed: () {
                                              setState(() {
                                                _obscurePassword =
                                                    !_obscurePassword;
                                              });
                                            },
                                          ),
                                          filled: true,
                                          fillColor: Colors.white,
                                          border: OutlineInputBorder(
                                            borderRadius: BorderRadius.circular(
                                              12,
                                            ),
                                            borderSide: BorderSide.none,
                                          ),
                                        ),
                                        enabled: !_isLoading,
                                      ),
                                    ),
                                    const SizedBox(height: 18),

                                    // Error message
                                    if (_errorMessage != null)
                                      Padding(
                                        padding: const EdgeInsets.only(
                                          bottom: 12.0,
                                        ),
                                        child: Text(
                                          _errorMessage!,
                                          style: const TextStyle(
                                            color: Colors.red,
                                          ),
                                        ),
                                      ),

                                    // Login Button
                                    ElevatedButton(
                                      style: ElevatedButton.styleFrom(
                                        backgroundColor: _isFormValid()
                                            ? Colors.green.shade700
                                            : Colors.grey.shade400,
                                        padding: const EdgeInsets.symmetric(
                                          vertical: 14,
                                        ),
                                        shape: RoundedRectangleBorder(
                                          borderRadius: BorderRadius.circular(
                                            12,
                                          ),
                                        ),
                                      ),
                                      onPressed: (_isLoading || !_isFormValid())
                                          ? null
                                          : _handleLogin,
                                      child: _isLoading
                                          ? const SizedBox(
                                              height: 18,
                                              width: 18,
                                              child: CircularProgressIndicator(
                                                color: Colors.white,
                                                strokeWidth: 2,
                                              ),
                                            )
                                          : const Text(
                                              'LOGIN',
                                              style: TextStyle(
                                                fontSize: 16,
                                                fontWeight: FontWeight.w600,
                                              ),
                                            ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 18),
                      // subtle footer
                      const Text(
                        'Secure inspections • QR-based • Offline friendly',
                        style: TextStyle(color: Colors.black45, fontSize: 12),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
