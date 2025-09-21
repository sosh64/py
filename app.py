from flask import Flask, request, render_template_string, url_for
import math
import random
import re
import os

app = Flask(__name__)

facts = [
    "Zero is the only number that can't be represented in Roman numerals.",
    "A circle has infinite lines of symmetry.",
    "Pi has been calculated to over 62 trillion digits.",
    "A googol is 10 to the power of 100.",
    "The Fibonacci sequence appears in nature, like in pinecones and sunflowers.",
    "An icosagon is a shape with 20 sides.",
    "There are infinitely many prime numbers.",
    "The number e is approximately 2.718 and is the base of natural logarithms.",
    "A perfect number is a number equal to the sum of its proper divisors (e.g., 28).",
    "The Pythagorean theorem only works in right-angled triangles.",
    "A palindrome number reads the same backward and forward (e.g., 121, 1331).",
    "The square root of 2 is irrational and cannot be written as a simple fraction.",
    "In base 2 (binary), only 1s and 0s are used to represent numbers.",
    "The golden ratio is approximately 1.618 and appears in art, architecture, and nature.",
    "A Möbius strip has only one surface and one edge.",
    "There are more real numbers between 0 and 1 than all whole numbers combined.",
    "The number 9 is known as a 'magic number' in many multiplication tricks.",
    "Euler’s identity combines five fundamental constants: e^(iπ) + 1 = 0.",
    "Kaprekar’s constant (6174) always appears in a specific subtraction trick.",
    "A prime number has exactly two distinct factors: 1 and itself.",
    "The sum of all angles in a triangle is always 180 degrees (in Euclidean geometry).",
    "You can tile a plane using only three regular polygons: triangles, squares, and hexagons.",
    "Infinity is not a number — it’s a concept representing something without end.",
    "The factorial of a number n (n!) is the product of all positive integers ≤ n.",
    "Magic squares are grids where the numbers in each row, column, and diagonal add up to the same total.",
    "An ellipse is the set of points where the sum of distances to two foci is constant."
]

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python Calculator</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        html, body { height: 100%; width: 100%; font-family: monospace, monospace; background-color: #f5f5f5; display: flex; justify-content: center; align-items: flex-start; padding: 20px; }
        .container { width: 100%; max-width: 600px; background: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); position: relative; }
        h1 { text-align: center; color: #333; margin-bottom: 20px; }
        .info { font-size: 0.9em; color: #666; margin-bottom: 15px; line-height: 1.4; }
        /* output wrapper to allow button pinned to its bottom-right */
        .output-wrap { position: relative; margin-bottom: 15px; }
        #output { white-space: pre-wrap; background: #f9f9f9; border: 1px solid #ddd; padding: 10px; height: 200px; overflow-y: auto; border-radius: 4px; }
        .output-pin-btn {
            position: absolute;
            right: 10px;
            bottom: 10px;
            background-color: #000;
            color: white;
            display: none; /* shown on mobile via media query */
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 10px;
            border-radius: 6px;
            text-decoration: none;
            font-size: 0.95em;
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        }
        .output-pin-btn svg { stroke: white; }

        input[type=text] { padding: 12px; font-size: 1.1em; border: 1px solid #ccc; border-radius: 4px; flex: 1; }
        button { padding: 12px; font-size: 1em; border: none; border-radius: 4px; background-color: #4CAF50; color: white; cursor: pointer; }
        button:hover { background-color: #45a049; }

        /* Desktop row with input + inline Updates button */
        .command-row {
            display: flex;
            gap: 10px;
        }
        .command-row .link-button {
            background-color: #000000;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 12px 16px;
            border-radius: 4px;
            text-decoration: none;
            font-size: 1em;
        }
        .command-row .link-button:hover {
            background-color: #333333;
        }
        .command-row .link-button svg {
            stroke: white;
        }

        /* Mobile: hide inline button, show pin-in-output button */
        @media (max-width: 768px) {
            .command-row .link-button {
                display: none;
            }
            .output-pin-btn {
                display: flex;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Python Calculator</h1>
        <div class="info">
            <strong>Commands:</strong><br>
            <b>/q</b> - Quit (clears output)<br>
            <b>/f</b> - Random math fact<br>
            <b>/e</b> - Random math equation<br>
            <b>/n</b> - Random number<br>
            more:<br>
            Check out my TikTok for easter eggs!<br>
            <b>Made by Giego :D</b>
        </div>

        <!-- output area with an output-pinned button that will appear at the bottom-right of this box on mobile -->
        <div class="output-wrap">
            <div id="output">{{ output|safe or "Welcome to Python Calculator!" }}</div>

            <!-- this button is pinned
