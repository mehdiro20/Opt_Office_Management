# -*- coding: utf-8 -*-
"""
Created on Thu Sep 11 04:10:53 2025

@author: Mehdi
"""

{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}My Website{% endblock %}</title>

  <style>
    /* Reset and layout */
    body {
      margin: 0;
      font-family: 'Segoe UI', Arial, sans-serif;
      display: flex;
      flex-direction: column;
      min-height: 100vh;
      background: #f4f6f8;
    }

    .content {
      flex: 1;
      padding: 20px;
      max-width: 1200px;
      margin: 0 auto;
    }

    /* Header */
    .site-header {
      background: #3498db;
      color: white;
      padding: 15px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .site-header .logo {
      margin: 0;
      font-size: 1.5rem;
      font-weight: bold;
    }
    .site-header nav a {
      color: white;
      text-decoration: none;
      margin: 0 12px;
      font-weight: 500;
    }
    .site-header nav a:hover {
      text-decoration: underline;
    }

    /* Footer */
    .site-footer {
      background: #2c3e50;
      color: white;
      text-align: center;
      padding: 20px 0;
      margin-top: auto;
    }
    .site-footer a {
      color: #1abc9c;
      text-decoration: none;
      margin: 0 8px;
      font-weight: 500;
    }
    .site-footer a:hover {
      text-decoration: underline;
    }
    .dashboard-link {
      display: inline-block;
      margin: 10px 0;
      padding: 8px 16px;
      border-radius: 6px;
      background: #1abc9c;
      color: white;
      text-decoration: none;
      font-weight: 600;
      transition: background 0.3s ease;
    }
    .dashboard-link:hover {
      background: #16a085;
    }
  </style>
</head>
<body>

  <!-- Header -->
  <header class="site-header">
    <h1 class="logo">My Website</h1>
    <nav>
      <a href="/">Home</a>
      <a href="/about/">About</a>
      <a href="/contact/">Contact</a>
    </nav>
  </header>

  <!-- Main content -->
  <main class="content">
    {% block content %}
    <!-- Page-specific content goes here -->
    {% endblock %}
  </main>

  <!-- Footer -->
  <footer class="site-footer">
    <div class="footer-container">
      <p>&copy; {{ now|date:"Y" }} My Website. All Rights Reserved.</p>
      
      {% if user.is_authenticated %}
        {% if role == "doctor" %}
          <a href="{% url 'doctor_dashboard' %}" class="dashboard-link">Go to Doctor Dashboard</a>
        {% elif role == "patient" %}
          <a href="{% url 'patient_dashboard' %}" class="dashboard-link">Go to Patient Dashboard</a>
        {% else %}
          <a href="{% url 'admin_dashboard' %}" class="dashboard-link">Go to Admin Dashboard</a>
        {% endif %}
      {% else %}
        <a href="{% url 'login' %}" class="dashboard-link">Login</a>
      {% endif %}

      <p>
        <a href="/about/">About</a> | 
        <a href="/contact/">Contact</a> | 
        <a href="/privacy/">Privacy Policy</a>
      </p>
    </div>
  </footer>

</body>
</html>
