# 1. Use Python 3.9
FROM python:3.9

# 2. Set up a secure user (Required by Hugging Face)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# 3. Set working directory
WORKDIR /app

# 4. Copy requirements and install them
COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application
COPY --chown=user . .

# 6. Open the port Hugging Face expects (7860)
EXPOSE 7860

# 7. Start the Flask app using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app", "--timeout", "120"]
