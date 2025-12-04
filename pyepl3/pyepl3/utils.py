"""
Utility functions for PyEPL3 experiments.

Common experimental tasks like math distractor.
"""

import random
import numpy as np
import pygame
from typing import Optional, List, Tuple

from .base import LogTrack, Registry
from .display import VideoTrack, Text, WHITE, BLACK, Color
from .keyboard import KeyTrack, Key, ButtonChooser
from .timing import PresentationClock, now


def mathDistract(clk: Optional[PresentationClock] = None,
                mathlog: Optional[LogTrack] = None,
                problemTimeLimit: Optional[int] = None,
                numVars: int = 2,
                maxNum: int = 9,
                minNum: int = 1,
                maxProbs: int = 50,
                plusAndMinus: bool = False,
                minDuration: Optional[int] = 20000,
                blanktime: int = 100,
                textSize: Optional[int] = None,
                tfKeys: Optional[Tuple[str, str]] = None,
                ansMod: List[int] = [0, 1, -1, 10, -10],
                ansProb: List[float] = [0.5, 0.125, 0.125, 0.125, 0.125]):
    """
    Math distractor task for experiments.

    Presents math problems for a minimum duration.
    Can be numeric answer or True/False format.

    Args:
        clk: PresentationClock
        mathlog: LogTrack for logging (optional, will create one if not provided)
        problemTimeLimit: Time limit per problem in ms (None = self-paced)
        numVars: Number of variables in each problem
        maxNum: Maximum number for variables
        minNum: Minimum number for variables
        maxProbs: Maximum number of problems
        plusAndMinus: Include subtraction (True) or just addition (False)
        minDuration: Minimum duration of distractor in ms
        blanktime: Time between problems in ms
        textSize: Font size (optional)
        tfKeys: Tuple of keys for T/F format, e.g., ('T', 'F')
        ansMod: Modifiers to add to correct answer for T/F problems
        ansProb: Probability of each modifier

    Returns:
        Number of problems completed
    """
    # Start timing
    start_time = now()

    # Get tracks
    video_instances = Registry.getInstances(VideoTrack)
    keyboard_instances = Registry.getInstances(KeyTrack)

    video = video_instances[-1] if video_instances else None
    keyboard = keyboard_instances[-1] if keyboard_instances else None

    if not video:
        raise ValueError("No VideoTrack found for mathDistract()")
    if not keyboard:
        raise ValueError("No KeyTrack found for mathDistract()")

    # Create math log if needed
    if mathlog is None:
        mathlog = LogTrack("math_distract")
        mathlog.startLogging()

    # Log start
    mathlog.logMessage("START")

    # Calculate stop time
    if minDuration:
        stop_time = start_time + minDuration
    else:
        stop_time = None

    # Generate math problems
    problems = []
    for _ in range(maxProbs):
        nums = np.random.randint(minNum, maxNum + 1, numVars)

        if plusAndMinus:
            ops = [random.choice(['+', '-']) for _ in range(numVars - 1)]
        else:
            ops = ['+'] * (numVars - 1)

        # Calculate answer
        result = nums[0]
        for i, op in enumerate(ops):
            if op == '+':
                result += nums[i + 1]
            else:
                result -= nums[i + 1]

        problems.append((nums, ops, result))

    # Determine if T/F or numeric
    if tfKeys and isinstance(tfKeys, tuple):
        tf_problems = True
        cumulative_prob = np.cumsum(ansProb)
    else:
        tf_problems = False

    # Run problems
    prob_count = 0
    print(f"\n=== STARTING DISTRACTOR: {maxProbs} problems ===")
    while (stop_time is None or now() < stop_time) and prob_count < len(problems):
        nums, ops, correct_answer = problems[prob_count]

        # Build problem string
        problem_str = str(nums[0])
        for i, op in enumerate(ops):
            problem_str += f" {op} {nums[i + 1]}"

        if tf_problems:
            # Choose a modifier
            rand_val = random.random()
            modifier = ansMod[0]
            for i, prob in enumerate(cumulative_prob):
                if rand_val < prob:
                    modifier = ansMod[i]
                    break

            displayed_answer = correct_answer + modifier
            problem_str += f" = {displayed_answer}"
            is_correct = (modifier == 0)
        else:
            problem_str += " = "

        # Show problem
        video.clear(BLACK)
        problem_text = Text(problem_str, size=textSize or 36, color=WHITE)
        video.showCentered(problem_text, clk)
        video.updateScreen(clk)

        # Get timestamp BEFORE waiting
        pres_time = clk.get() if clk else now()

        # Wait for response
        if tf_problems:
            bc = ButtonChooser(Key(tfKeys[0]), Key(tfKeys[1]), track=keyboard)
            if problemTimeLimit:
                button, timestamp = bc.waitWithTime(clk, timeout=problemTimeLimit)
            else:
                button, timestamp = bc.waitWithTime(clk)

            # Log T/F response
            if button:
                response = button.key_name
                user_says_true = (response == tfKeys[0])
                response_correct = (user_says_true == is_correct)
                mathlog.logMessage(f"PROBLEM\t{problem_str}\t{response}\t{response_correct}")
            else:
                mathlog.logMessage(f"PROBLEM\t{problem_str}\tTIMEOUT")
        else:
            # Numeric mode: time-locked input with visual feedback
            rstr = ""  # User's typed answer
            has_minus = False

            # Create ButtonChooser for all numeric input keys
            numeric_keys = [Key(str(d)) for d in range(10)]  # 0-9
            numeric_keys.append(Key("-"))  # minus key
            numeric_keys.append(Key("BACKSPACE"))
            bc = ButtonChooser(*numeric_keys, track=keyboard)

            # Calculate end time for this problem
            if problemTimeLimit:
                prob_end = pres_time + problemTimeLimit
            else:
                prob_end = None  # No timeout

            # Time-locked input loop
            while True:
                # Calculate remaining time
                current_time = clk.get() if clk else now()
                if prob_end is not None:
                    remaining = prob_end - current_time
                    if remaining <= 0:
                        break  # Timeout reached
                else:
                    remaining = None

                # Wait for keypress
                button, timestamp = bc.waitWithTime(clk, timeout=remaining)

                if button is None:
                    # Timeout
                    break

                # Process the keypress
                key_name = button.key_name

                if key_name == "BACKSPACE":
                    if len(rstr) > 0:
                        rstr = rstr[:-1]
                        if len(rstr) == 0:
                            has_minus = False
                elif key_name == "MINUS" or key_name == "-":
                    if len(rstr) == 0 and plusAndMinus:
                        rstr = "-"
                        has_minus = True
                elif key_name.isdigit():
                    # Don't allow leading zero
                    if len(rstr) == 0 and key_name == "0":
                        pass  # Can't start with 0
                    elif has_minus and len(rstr) == 1 and key_name == "0":
                        pass  # Can't have -0
                    else:
                        rstr = rstr + key_name

                # Update display with current answer
                video.clear(BLACK)
                display_str = problem_str + rstr
                display_text = Text(display_str, size=textSize or 36, color=WHITE)
                video.showCentered(display_text, clk)
                video.updateScreen(clk)

            # Score the answer
            try:
                user_answer = int(rstr) if rstr and rstr != "-" else None
                response_correct = 1 if user_answer == correct_answer else 0
            except ValueError:
                user_answer = None
                response_correct = 0

            # Log numeric response
            mathlog.logMessage(f"PROBLEM\t{problem_str}{rstr}\t{rstr}\t{response_correct}")
            correct_str = "correct" if response_correct else "incorrect"
            print(f"[DIST] Problem {prob_count + 1}/{maxProbs}: {problem_str}{correct_answer} | Answer: {rstr or 'none'} | {correct_str}")

        # Blank screen between problems
        video.clear(BLACK)
        video.updateScreen(clk)
        if clk:
            clk.delay(blanktime)

        # Clear pygame event queue to prevent buildup between problems
        pygame.event.clear()

        prob_count += 1

    print(f"=== DISTRACTOR COMPLETE: {prob_count} problems ===\n")

    # Log end
    mathlog.logMessage("END")

    # Clear screen
    video.clear(BLACK)
    video.updateScreen(clk)

    return prob_count
