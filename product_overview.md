# 📘 Product Overview: Ariel CS 2026 Agent

**Version:** 1.0 (MVP)
**Status:** In Development
**Developer:** Nitay Caspi

## 1\. Executive Summary

The **Ariel CS 2026 Agent** is an AI-powered Telegram bot designed specifically for first-year Computer Science students at Ariel University. Unlike generic AI chatbots, this agent utilizes **RAG (Retrieval-Augmented Generation)** to provide accurate, context-aware answers based on the specific university syllabus, lecture notes, and past exams. It acts as a 24/7 virtual Teaching Assistant, bridging the gap between overwhelming academic material and student success.

## 2\. The Problem

First-year CS students often face "Academic Shock":

  * **Information Overload:** Hundreds of PDFs, presentations, and administrative rules scattered across different platforms.
  * **High Difficulty Curve:** Courses like Calculus (Infinitesimal) and Linear Algebra require immediate, personalized feedback that human TAs cannot always provide.
  * **Accessibility:** existing solutions (Moodle, Drive) are passive; students have to search for information rather than ask for it.

## 3\. The Solution

An intelligent, proactive agent that lives where the students already are—**Telegram**.

### Core Value Proposition

  * **Contextual Accuracy:** The bot doesn't just "guess" math; it answers based on the specific PDFs uploaded by the department.
  * **Multimodal Support:** Students can snap a picture of a whiteboard or a notebook, and the AI will analyze and explain the solution.
  * **Instant Availability:** Reduces dependency on human TAs for repetitive questions.

## 4\. Key Features (MVP)

### 📚 A. The Academic Brain (RAG)

  * **Document Search:** The bot is connected to a managed Vector Store containing course materials (e.g., "Intro to CS," "Calculus 1").
  * **Citation:** Answers include references to the source material (e.g., *"According to Lecture 5 summary..."*).

### 👁️ B. Vision Helper

  * **Snap & Solve:** Users send an image of a handwritten exercise. The bot utilizes Gemini 1.5 Flash Vision capabilities to recognize the handwriting, transcribe the math to LaTeX, and explain the solution step-by-step.

### 🛡️ C. Secure Access (Gatekeeping)

  * **Exclusive Community:** To prevent abuse and manage API costs, the bot is protected by a password system.
  * **User Allow-list:** Only verified students (who input the correct class password) gain persistent access to the bot's features.

## 5\. Technical Architecture

  * **Interface:** Telegram Bot API (Python).
  * **LLM Engine:** Google Gemini 1.5 Flash (chosen for speed, cost-efficiency, and large context window).
  * **Knowledge Base:** Google File Search (Managed Vector Store).
  * **Backend Logic:** Python 3.x with asynchronous handling.

## 6\. Target Audience (User Persona)

**"Dan the Freshman"**

  * **Age:** 21-24.
  * **Pain Point:** Stuck on a Calculus limit problem at 11:00 PM the night before a quiz.
  * **Goal:** Wants a quick explanation of the "Sandwich Theorem" based on how *his* professor explained it, not a random Wikipedia definition.
  * **Usage:** Opens Telegram, types "Explain the Sandwich Theorem based on the summary," and gets an instant answer.

## 7\. Future Roadmap (Post-MVP)

  * **Quiz Mode:** The bot actively generates multiple-choice questions to test the student's knowledge.
  * **Schedule Integration:** Connecting to the university calendar to remind students of submission deadlines.
  * **Voice Interface:** Allowing students to send voice notes ("Explain this code") and receive audio responses.
