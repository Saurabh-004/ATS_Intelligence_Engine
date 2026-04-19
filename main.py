from fastapi import FastAPI
from routes import router as predict_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(predict_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)






"""House Price Prediction Platform (End-to-End, Deployed) Python, Scikit-learn, Flask, Pandas,
NumPy, Render
2025
• Built an end-to-end regression system for house price prediction covering data preprocessing, feature
engineering, model training, and inference.
• Performed exploratory data analysis, outlier detection, and error analysis to improve generalization
across unseen samples.
• Deployed a production-ready web application on Render, exposing trained models via Flask with
reproducible pipelines and documentation.
Language Modeling using GRU (From Scratch) Python, PyTorch, GRU, Backpropagation
Through Time
2025
• Implemented a GRU-based language model from scratch without using high-level PyTorch
RNN abstractions.
• Manually defined update gate, reset gate, candidate hidden state, and hidden state transitions.
• Trained the model on textual data using custom training loops, PyTorch loss functions, and
backpropagation through time.
Fake News Classification using Word Embeddings Python, spaCy, Scikit-learn, Linear SVM
2024
• Built a binary text classification system to detect fake vs real news articles using pre-trained spaCy
word embeddings.
• Cleaned and analyzed a 22K-sample dataset; removed 8% duplicate samples to prevent data
leakage.
• Achieved 99% precision and recall on a stratified test set using Linear SVM.
• Evaluated model performance using classification reports and confusion matrices to validate
robustness.
Education
Chandigarh University
Bachelor of Computer Applications (BCA)– CGPA: 8.03
IIT Madras
BS in Data Science and Applications– CGPA: 7.2
Technical Skills
Aug 2023– Jul 2026
Mohali, India
Aug 2023– Jul 2027
Online
Programming & Libraries: Python, NumPy, Pandas, Scikit-learn, PyTorch, Tensorflow, spaCy
Machine Learning & NLP: Regression, Classification, Feature Engineering, Model Evaluation,
Word Embeddings, Text Classification, Language Modeling, Sequence Modeling
Deep Learning: Neural Networks, CNNs, RNNs, GRU, Backpropagation Through Time
Deployment & Tools: Flask, FastAPI (basic), Git, GitHub, Linux, MLflow (basic)
Foundations: Probability, Statistics, Linear Algebra, Optimization
Certifications
• Foundation in Data Science– IIT Madras
• Advanced Python Programming– Coursera
• Generative AI Fundamentals– Courser"""


"""Strong proficiency in Python is required, along with experience in languages like Java or C++, and familiarity with other languages like R is a plus. AI/ML Concepts: Solid understanding of fundamental AI and machine learning concepts, including algorithms for classification, regression, and clustering. AI Specialization: Proven experience in one or more areas, including: Natural Language Processing (NLP): Experience with transformers, LLMs, LangChain, and RAG techniques. Computer Vision (CV): Experience with CNNs and tools like OpenCV. Reinforcement Learning (RL): Experience with algorithms like Q-learning and Policy Gradients. Generative AI: Experience in developing and fine-tuning generative models and implementing agentic AI systems. Frameworks & Libraries: Experience with deep learning frameworks such as TensorFlow or PyTorch, and a working knowledge of Python libraries like scikit-learn, NumPy, and pandas. MLOps: Solid understanding and practical experience with MLOps concepts, including CI/CD pipelines, Docker, and Kubernetes. Cloud Platforms: Experience with cloud computing services like AWS, Google Cloud Platform, or Microsoft Azure for deploying and scaling AI models. Data and Databases: Experience with data processing libraries like PySpark and big data technologies such as Hadoop. Knowledge of SQL and NoSQL databases. APIs: Experience designing and developing APIs (e.g., using Flask or FastAPI) to serve AI models. Data Handling: Hands-on experience with data manipulation and analysis is essential. Specialization (Nice-to-have): Familiarity with specific AI domains like Natural Language Processing (NLP), Computer Vision (CV), or Generative AI is a plus. Cloud (Nice-to-have): Exposure to cloud platforms like AWS, Google Cloud Platform, or Azure is beneficial."""