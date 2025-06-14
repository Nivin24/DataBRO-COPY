const startButton = document.getElementById('start-btn');
const questionContainer = document.getElementById('question-container');
questionContainer.classList.add('hide');
const questionElement = document.getElementById('question');
const answerButtonsElement = document.getElementById('answer-buttons');
const scoreContainer = document.getElementById('score-container');
const timerElement = document.getElementById('timer');
const resultContainer = document.getElementById('result-container');

let currentQuestionIndex = 0;
let score = 0;
let timer = null;
let timeLeft = 15; // seconds per question
let selectedQuestions = [];
let userAnswers = [];

// Example questions array (replace with your actual questions)
const questions = [
    { 
        question: "What is the correct file extension for Python files?", 
        answers: [
            { text: ".py", correct: true },
            { text: ".python", correct: false },
            { text: ".pt", correct: false },
            { text: ".pyt", correct: false }
        ]
    },
    { 
        question: "Which keyword is used to create a function in Python?", 
        answers: [
            { text: "function", correct: false },
            { text: "define", correct: false },
            { text: "def", correct: true },
            { text: "fun", correct: false }
        ]
    },
    { 
        question: "What is the output of: print(type(5))?", 
        answers: [
            { text: "<type 'float'>", correct: false },
            { text: "<type 'string'>", correct: false },
            { text: "<type 'int'>", correct: true },
            { text: "<type 'bool'>", correct: false }
        ]
    },
    { 
        question: "Which of these is a Python data type?", 
        answers: [
            { text: "character", correct: false },
            { text: "decimal", correct: false },
            { text: "tuple", correct: true },
            { text: "real", correct: false }
        ]
    },
    { 
        question: "What is the correct way to create a list in Python?", 
        answers: [
            { text: "list = (1, 2, 3)", correct: false },
            { text: "list = [1, 2, 3]", correct: true },
            { text: "list = {1, 2, 3}", correct: false },
            { text: "list = <1, 2, 3>", correct: false }
        ]
    },
    { 
        question: "Which operator is used for exponentiation in Python?", 
        answers: [
            { text: "^", correct: false },
            { text: "**", correct: true },
            { text: "^^", correct: false },
            { text: "//", correct: false }
        ]
    },
    { 
        question: "What is the output of: print(10 // 3)?", 
        answers: [
            { text: "3.33", correct: false },
            { text: "3", correct: true },
            { text: "4", correct: false },
            { text: "10", correct: false }
        ]
    },
    { 
        question: "Which of the following is used to handle exceptions in Python?", 
        answers: [
            { text: "try...catch", correct: false },
            { text: "handle...except", correct: false },
            { text: "try...except", correct: true },
            { text: "do...except", correct: false }
        ]
    },
    { 
        question: "What does the len() function do?", 
        answers: [
            { text: "Returns last element", correct: false },
            { text: "Returns type of list", correct: false },
            { text: "Returns length", correct: true },
            { text: "Reverses list", correct: false }
        ]
    },
    { 
        question: "Which keyword is used for loops in Python?", 
        answers: [
            { text: "repeat", correct: false },
            { text: "for", correct: true },
            { text: "iterate", correct: false },
            { text: "loop", correct: false }
        ]
    },
    { 
        question: "How do you insert COMMENTS in Python code?", 
        answers: [
            { text: "// comment", correct: false },
            { text: "<!-- comment -->", correct: false },
            { text: "# comment", correct: true },
            { text: "/* comment */", correct: false }
        ]
    },
    { 
        question: "What data type is the result of: 3 > 2?", 
        answers: [
            { text: "int", correct: false },
            { text: "bool", correct: true },
            { text: "float", correct: false },
            { text: "string", correct: false }
        ]
    },
    { 
        question: "Which of these is used to define a dictionary?", 
        answers: [
            { text: "{}", correct: true },
            { text: "[]", correct: false },
            { text: "()", correct: false },
            { text: "<>", correct: false }
        ]
    },
    { 
        question: "Which of these is immutable?", 
        answers: [
            { text: "list", correct: false },
            { text: "set", correct: false },
            { text: "tuple", correct: true },
            { text: "dict", correct: false }
        ]
    },
    { 
        question: "How do you start a class definition in Python?", 
        answers: [
            { text: "define class", correct: false },
            { text: "class()", correct: false },
            { text: "class", correct: true },
            { text: "new class", correct: false }
        ]
    },
    { 
        question: "What does the range(5) function return?", 
        answers: [
            { text: "[1,2,3,4,5]", correct: false },
            { text: "[0,1,2,3,4]", correct: true },
            { text: "[0,1,2,3,4,5]", correct: false },
            { text: "[1,2,3,4]", correct: false }
        ]
    },
    { 
        question: "Which function is used to get user input?", 
        answers: [
            { text: "get()", correct: false },
            { text: "input()", correct: true },
            { text: "read()", correct: false },
            { text: "user_input()", correct: false }
        ]
    },
    { 
        question: "What is the result of: len('Python')?", 
        answers: [
            { text: "5", correct: false },
            { text: "7", correct: false },
            { text: "6", correct: true },
            { text: "Error", correct: false }
        ]
    },
    { 
        question: "Which keyword is used to define a loop that runs until a condition is false?", 
        answers: [
            { text: "repeat", correct: false },
            { text: "do", correct: false },
            { text: "while", correct: true },
            { text: "until", correct: false }
        ]
    },
    { 
        question: "What does the strip() method do?", 
        answers: [
            { text: "Removes spaces", correct: true },
            { text: "Changes case", correct: false },
            { text: "Finds substrings", correct: false },
            { text: "Adds dashes", correct: false }
        ]
    },
    { 
        question: "Which of these is a valid variable name?", 
        answers: [
            { text: "1st_variable", correct: false },
            { text: "first-variable", correct: false },
            { text: "firstVariable", correct: false },
            { text: "_firstVariable", correct: true }
        ]
    },
    { 
        question: "What is the output of: print('Hello' + 'World')?", 
        answers: [
            { text: "Hello World", correct: false },
            { text: "HelloWorld", correct: true },
            { text: "Error", correct: false },
            { text: "Hello+World", correct: false }
        ]
    },
    { 
        question: "Which of these is a Python library for data manipulation?", 
        answers: [
            { text: "NumPy", correct: false },
            { text: "Pandas", correct: true },
            { text: "Matplotlib", correct: false },
            { text: "SciPy", correct: false }
        ]
    },
    { 
        question: "What is the output of: print(2 * 3 ** 2)?", 
        answers: [
            { text: "18", correct: false },
            { text: "12", correct: true },
            { text: "9", correct: false },
            { text: "6", correct: false }
        ]
    },
    { 
        question: "Which of these is a Python web framework?", 
        answers: [
            { text: "Django", correct: false },
            { text: "Flask", correct: false },
            { text: "Pyramid", correct: false },
            { text: "All of the above", correct: true }
        ]
    },
    { 
        question: "What is the output of: print('a' in 'apple')?", 
        answers: [
            { text: "True", correct: true },
            { text: "False", correct: false },
            { text: "Error", correct: false },
            { text: "None", correct: false }
        ]
    },
    { 
        question: "Which of these is a Python library for data visualization?", 
        answers: [
            { text: "NumPy", correct: false },
            { text: "Pandas", correct: false },
            { text: "Matplotlib", correct: true },
            { text: "SciPy", correct: false }
        ]
    },
    { 
        question: "What is the output of: print('Hello'.upper())?", 
        answers: [
            { text: "hello", correct: false },
            { text: "HELLO", correct: true },
            { text: "Hello", correct: false },
            { text: "Error", correct: false }
        ]
    },
    { 
        question: "Which of these is a Python library for machine learning?", 
        answers: [
            { text: "NumPy", correct: false },
            { text: "Pandas", correct: false },
            { text: "Scikit-learn", correct: true },
            { text: "SciPy", correct: false }
        ]
    },
    { 
        question: "What is the output of: print('Hello'.replace('l', 'x'))?", 
        answers: [
            { text: "Hexxo", correct: true },
            { text: "Hexlo", correct: false },
            { text: "Hello", correct: false },
            { text: "Error", correct: false }
        ]
    },
    { 
        question: "Which of these is a Python library for numerical computations?", 
        answers: [
            { text: "NumPy", correct: true },
            { text: "Pandas", correct: false },
            { text: "Matplotlib", correct: false },
            { text: "SciPy", correct: false }
        ]
    },
    { 
        question: "What is the output of: print(5 == 5.0)?", 
        answers: [
            { text: "True", correct: true },
            { text: "False", correct: false },
            { text: "Error", correct: false },
            { text: "None", correct: false }
        ]
    },
    { 
        question: "Which of these is a Python library for scientific computing?", 
        answers: [
            { text: "NumPy", correct: false },
            { text: "Pandas", correct: false },
            { text: "Matplotlib", correct: false },
            { text: "SciPy", correct: true }
        ]
    },
    { 
        question: "What is the output of: print('Hello'.find('l'))?", 
        answers: [
            { text: "2", correct: true },
            { text: "3", correct: false },
            { text: "-1", correct: false },
            { text: "Error", correct: false }
        ]
    },
    { 
        question: "Which of these is a Python library for data analysis?", 
        answers: [
            { text: "NumPy", correct: false },
            { text: "Pandas", correct: true },
            { text: "Matplotlib", correct: false },
            { text: "SciPy", correct: false }
        ]
    },
    { 
        question: "What is the output of: print(10 % 3)?", 
        answers: [
            { text: "1", correct: true },
            { text: "3", correct: false },
            { text: "0", correct: false },
            { text: "2", correct: false }
        ]
    },
    { 
        question: "Which of these is a Python library for image processing?", 
        answers: [
            { text: "NumPy", correct: false },
            { text: "PIL", correct: true },
            { text: "Matplotlib", correct: false },
            { text: "SciPy", correct: false }
        ]
    }
];

startButton.addEventListener('click', startQuiz);

function startQuiz() {
    startButton.classList.add('hide');
    resultContainer.classList.add('hide');
    questionContainer.classList.remove('hide');
    timerElement.classList.remove('hide'); // Ensure the timer is visible
    currentQuestionIndex = 0;
    score = 0;
    userAnswers = [];

    // Populate selectedQuestions with 20 random questions
    selectedQuestions = shuffleArray(questions).slice(0, 10); // Adjust the number of questions here
    setNextQuestion();
}

function shuffleArray(array) {
    return array.sort(() => Math.random() - 0.5);
}

function resetState() {
    clearInterval(timer); // Clear the timer if it's running
    timeLeft = 15; // Reset timer for the next question
    answerButtonsElement.innerHTML = '';
    clearStatusClass(document.body);
}

function setNextQuestion() {
    resetState();
    if (currentQuestionIndex < selectedQuestions.length) {
        showQuestion(selectedQuestions[currentQuestionIndex]);
        startTimer();
    } else {
        showResult();
    }
}

function showQuestion(question) {
    questionElement.innerText = question.question;
    answerButtonsElement.innerHTML = '';
    question.answers.forEach((answer, idx) => {
        const button = document.createElement('button');
        button.innerText = answer.text;
        button.classList.add('btn');
        button.dataset.correct = answer.correct;
        button.dataset.index = idx;
        button.addEventListener('click', () => selectAnswer(answer, button)); // Use this here
        answerButtonsElement.appendChild(button);
    });
    timerElement.textContent = `Time left: ${timeLeft}s`;
}

function startTimer() {
    timerElement.textContent = `Time left: ${timeLeft}s`;
    timer = setInterval(() => {
        timeLeft--;
        timerElement.textContent = `Time left: ${timeLeft}s`;
        if (timeLeft === 0) {
            clearInterval(timer);
            handleTimeOut();
        }
    }, 1000);
}


function selectAnswer(answer, selectedButton) {
    clearInterval(timer);
    const correct = answer.correct;
    setStatusClass(selectedButton, correct);
    if (correct) score++;
    // Store the index of the selected answer for review
    userAnswers[currentQuestionIndex] = parseInt(selectedButton.dataset.index, 10);
    Array.from(answerButtonsElement.children).forEach(button => {
        const isCorrect = selectedQuestions[currentQuestionIndex].answers.find(a => a.text === button.innerText).correct;
        setStatusClass(button, isCorrect);
        button.disabled = true;
    });
    // Automatically move to the next question after 2 seconds
    setTimeout(autoNextQuestion, 1000);
}

function autoNextQuestion() {
    currentQuestionIndex++;
    if (currentQuestionIndex < selectedQuestions.length) {
        setNextQuestion();
    } else {
        showResult();
    }
}

function handleTimeOut() {
    userAnswers[currentQuestionIndex] = null;
    Array.from(answerButtonsElement.children).forEach((button) => {
        setStatusClass(button, button.dataset.correct === "true");
        button.disabled = true;
    });
    // Automatically move to the next question after 2 seconds
    setTimeout(autoNextQuestion, 2000);
}

function showResult() {
    clearInterval(timer); // Ensure timer is stopped before showing result
    startButton.classList.add('hide');
    questionContainer.classList.add('hide');
    scoreContainer.classList.add('hide');
    questionElement.textContent = 'Quiz Completed!';
    answerButtonsElement.innerHTML = '';
    document.body.style.overflow = ''; // Remove any overflow style applied to the body
    // Hide the page heading
    document.getElementById('page-heading').classList.add('hide');
    // Show score and message

    timerElement.textContent = '';
    let message = '';
    if (score <= 10) {
        message = `You scored ${score}/${selectedQuestions.length}. Don't worry — every master was once a beginner. Keep learning! 🚀`;
    } else if (score <= 17) {
        message = `You scored ${score}/${selectedQuestions.length}. Great job! You're a few steps away from mastery. Keep up the momentum! 💪`;
    } else {
        message = `You scored ${score}/${selectedQuestions.length}. You're a Python Wizard! 🧙‍♂️ Keep casting your code spells!`;
    }

    // Save history to localStorage
    const history = JSON.parse(localStorage.getItem("quizHistory") || "[]");
    history.push({
        date: new Date().toLocaleString(),
        score: `${score}/${selectedQuestions.length}`
    });
    localStorage.setItem("quizHistory", JSON.stringify(history));

    // Review
    let reviewHtml = `<ul style="text-align: left; padding-left: 20px;">`;
    selectedQuestions.forEach((q, idx) => {
        const correctIndex = q.answers.findIndex(a => a.correct);
        const userIndex = userAnswers[idx];
        let isCorrect = false;
        let userAnswerText = "No answer";
        if (
            Array.isArray(q.answers) &&
            typeof userIndex === "number" &&
            userIndex >= 0 &&
            userIndex < q.answers.length
        ) {
            userAnswerText = q.answers[userIndex].text;
            isCorrect = userIndex === correctIndex;
        }
        let correctAnswerText = (Array.isArray(q.answers) && correctIndex >= 0 && correctIndex < q.answers.length)
            ? q.answers[correctIndex].text
            : "N/A";
        reviewHtml += `
            <li style="margin-bottom: 10px;">
                <strong>Q${idx + 1}:</strong> ${q.question}<br>
                <span style="color: ${isCorrect ? 'green' : 'red'};">
                    Your answer: ${userAnswerText}
                </span><br>
                <span style="color: green;">
                    Correct answer: ${correctAnswerText}
                </span>
            </li>
        `;
    });
    reviewHtml += `</ul>`;
    resultContainer.classList.remove('hide');
    const isDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;

    const backgroundColor = isDarkMode ? '#333' : '#fafafa';
    const textColor = isDarkMode ? '#fafafa' : '#333';
    const borderColor = isDarkMode ? '#555' : '#ccc';

    resultContainer.innerHTML = `
    <div class="result-box" style="display: flex; flex-direction: column; align-items: center; width: 100%; max-width: 600px; margin: 0 auto; box-sizing: border-box; padding: 16px; background: ${backgroundColor}; color: ${textColor}; border-radius: 8px;">
        <h2 style="font-size: 1.5em; text-align: center; word-break: break-word;">${message}</h2>
        <div style="width: 100%; margin-top: 20px;">
            <h3 style="text-align: left;">Review:</h3>
            <div style="
                width: 100%;
                max-height: 40vh;
                min-height: 120px;
                overflow-y: auto;
                border: 1px solid ${borderColor};
                padding: 10px;
                border-radius: 5px;
                background: ${isDarkMode ? '#444' : '#fff'};
                box-sizing: border-box;
            ">
                <ol style="padding-left: 20px; margin: 0;">
                    ${reviewHtml}
                </ol>
            </div>
        </div>
        <div style="width: 100%; margin-top: 20px; display: flex; justify-content: center;">
            <button id="restart-btn" class="btn" style="width: 100%; max-width: 250px; background: ${isDarkMode ? '#555' : '#ddd'}; color: ${textColor}; border: 1px solid ${borderColor};">Restart Quiz</button>
        </div>
    </div>
    <style>
    @media (max-width: 600px) {
        .result-box {
            max-width: 98vw !important;
            padding: 0 2vw !important;
        }
        .result-box h2, .result-box h3 {
            font-size: 1.1em !important;
        }
    }
    #result-container {
        width: 100vw;
        min-height: 100vh;
        max-height: 100vh;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        box-sizing: border-box;
        padding: 0;
        margin: 0;
        background: ${backgroundColor};
        color: ${textColor};
    }
    </style>
    `;

    document.getElementById('restart-btn').onclick = restartQuiz;
}

function restartQuiz() {
    currentQuestionIndex = 0;
    score = 0;
    userAnswers = [];
    resultContainer.classList.add('hide');
    // Show the page heading
    document.getElementById('page-heading').classList.remove('hide');
    clearTimer(); // Ensure the timer is cleared when restarting
    startQuiz();
}

function setStatusClass(element, correct) {
    clearStatusClass(element);
    if (correct) {
        element.classList.add('correct');
    } else {
        element.classList.add('wrong');
    }
}

function clearStatusClass(element) {
    element.classList.remove('correct');
    element.classList.remove('wrong');
}

// Add this function to clear the timer when the quiz is restarted
function clearTimer() {
    clearInterval(timer);
    timer = null;
    timeLeft = 15; // Reset timer for the next question
}

