document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const uploadForm = document.getElementById('upload-form');
    const urlForm = document.getElementById('url-form');
    const uploadBtn = document.getElementById('upload-btn');
    const urlBtn = document.getElementById('url-btn');
    const uploadSpinner = document.getElementById('upload-spinner');
    const urlSpinner = document.getElementById('url-spinner');
    const uploadStatus = document.getElementById('upload-status');
    const progressContainer = document.getElementById('progress-container');
    const progressLabel = document.getElementById('progress-label');
    const uploadProgress = document.getElementById('upload-progress');
    const questionForm = document.getElementById('question-form');
    const questionInput = document.getElementById('question-input');
    const askBtn = document.getElementById('ask-btn');
    const askSpinner = document.getElementById('ask-spinner');
    const chatContainer = document.getElementById('chat-container');
    const sampleQuestions = document.getElementById('sample-questions');
    const questionsList = document.getElementById('questions-list');
    const visitorCountElement = document.getElementById('visitor-count');
    const requestLimitContainer = document.getElementById('request-limit-container');
    const requestLimitCounter = document.getElementById('request-limit-counter');
    
    // State variables
    let documentUploaded = false;
    let remainingRequests = 5;
    
    // Check for visitor count updates every minute
    setInterval(updateVisitorCount, 60000);
    
    // Check remaining requests on page load
    checkRemainingRequests();

    // Handle document upload
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const fileInput = document.getElementById('document');
        const file = fileInput.files[0];
        
        if (!file) {
            showUploadStatus('Please select a file to upload.', 'danger');
            return;
        }
        
        // Check file type
        if (!file.name.endsWith('.txt') && !file.name.endsWith('.pdf')) {
            showUploadStatus('Only .txt and .pdf files are supported.', 'danger');
            return;
        }
        
        // Show spinner and disable button
        uploadSpinner.classList.remove('d-none');
        uploadBtn.disabled = true;
        
        // Show progress bar
        progressLabel.textContent = "Processing document...";
        progressContainer.style.display = 'block';
        
        // Progress animation
        let progress = 0;
        const progressInterval = setInterval(() => {
            // Increment progress, but not to 100% until we get a response
            if (progress < 90) {
                progress += 5;
                uploadProgress.style.width = `${progress}%`;
            }
        }, 300);
        
        // Create form data
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            // Set progress to 100% when response is received
            clearInterval(progressInterval);
            uploadProgress.style.width = '100%';
            
            // Delay hiding progress bar for visual effect
            setTimeout(() => {
                progressContainer.style.display = 'none';
                uploadProgress.style.width = '0%';
            }, 500);
            
            const data = await response.json();
            
            if (response.ok) {
                showUploadStatus(data.message, 'success');
                documentUploaded = true;
                
                // Enable the question input and button
                questionInput.disabled = false;
                askBtn.disabled = false;
                
                // Clear previous chat
                chatContainer.innerHTML = '';
                
                // Add welcome message from Joco
                showChatMessage('Document processed successfully! I\'m ready to answer your questions about the content.', 'bot');
                
                // Display sample questions
                displaySampleQuestions(data.sample_questions);
            } else {
                showUploadStatus(data.detail || 'Upload failed.', 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            showUploadStatus('An error occurred while uploading the document.', 'danger');
            
            // Stop progress animation
            clearInterval(progressInterval);
            progressContainer.style.display = 'none';
            uploadProgress.style.width = '0%';
        } finally {
            // Hide spinner and enable button
            uploadSpinner.classList.add('d-none');
            uploadBtn.disabled = false;
        }
    });
    
    // Handle URL form submission
    urlForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const urlInput = document.getElementById('website-url');
        const url = urlInput.value.trim();
        
        if (!url) {
            showUploadStatus('Please enter a website URL.', 'danger');
            urlInput.classList.add('shake-animation');
            setTimeout(() => {
                urlInput.classList.remove('shake-animation');
            }, 820);
            return;
        }
        
        // Show spinner and disable button
        urlSpinner.classList.remove('d-none');
        urlBtn.disabled = true;
        urlInput.disabled = true;
        
        // Show progress bar with fade-in
        progressLabel.textContent = "Fetching website content...";
        progressContainer.style.display = 'block';
        progressContainer.classList.add('fade-in');
        
        // Progress animation with variable speed
        let progress = 0;
        let randomFactor = 1;
        const progressInterval = setInterval(() => {
            // Randomize progress speed a bit to make it look more natural
            randomFactor = 0.5 + Math.random();
            
            // Increment progress, but not to 100% until we get a response
            if (progress < 90) {
                // Slower than file upload since web scraping takes longer
                // Speed up initially, then slow down
                let increment = progress < 30 ? 5 * randomFactor : 2 * randomFactor;
                progress += increment;
                uploadProgress.style.width = `${progress}%`;
                
                // Add "thinking" periods to the label as time passes
                if (progress > 40 && progress < 60) {
                    progressLabel.textContent = "Analyzing content...";
                } else if (progress > 60 && progress < 80) {
                    progressLabel.textContent = "Processing text...";
                } else if (progress > 80) {
                    progressLabel.textContent = "Finalizing...";
                }
            }
        }, 300);
        
        try {
            const response = await fetch('/process-url', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url })
            });
            
            // Set progress to 100% when response is received
            clearInterval(progressInterval);
            uploadProgress.style.width = '100%';
            progressLabel.textContent = "Complete!";
            
            // Delay hiding progress bar for visual effect
            setTimeout(() => {
                progressContainer.classList.add('fade-out');
                setTimeout(() => {
                    progressContainer.style.display = 'none';
                    progressContainer.classList.remove('fade-out');
                    uploadProgress.style.width = '0%';
                }, 300);
            }, 800);
            
            const data = await response.json();
            
            if (response.ok) {
                showUploadStatus(data.message, 'success');
                documentUploaded = true;
                
                // Only re-enable if we still have requests left
                if (remainingRequests > 0) {
                    questionInput.disabled = false;
                    askBtn.disabled = false;
                }
                
                // Clear previous chat
                chatContainer.innerHTML = '';
                
                // Add welcome message from Joco
                showChatMessage(`Website content processed successfully! I've analyzed content from ${url} and I'm ready to answer your questions.`, 'bot');
                
                // Display sample questions with staggered animation
                displaySampleQuestions(data.sample_questions, true);
                
                // Check remaining requests on successful upload
                checkRemainingRequests();
                
                // Clear the URL input
                urlInput.value = '';
            } else {
                showUploadStatus(data.detail || 'Failed to process website.', 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            showUploadStatus('An error occurred while processing the website.', 'danger');
            
            // Stop progress animation
            clearInterval(progressInterval);
            progressContainer.style.display = 'none';
            uploadProgress.style.width = '0%';
        } finally {
            // Hide spinner and enable button
            urlSpinner.classList.add('d-none');
            urlBtn.disabled = false;
            urlInput.disabled = false;
        }
    });

    // Handle question submission
    questionForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const question = questionInput.value.trim();
        
        if (!question) {
            return;
        }
        
        if (!documentUploaded) {
            showChatMessage('Please upload a document first.', 'bot');
            questionInput.classList.add('shake-animation');
            setTimeout(() => {
                questionInput.classList.remove('shake-animation');
            }, 820);
            return;
        }
        
        // Check if user has hit their request limit
        if (remainingRequests <= 0) {
            showChatMessage('You have reached your limit of 10 questions. Please try again later.', 'bot');
            return;
        }
        
        // Show spinner and disable button
        askSpinner.classList.remove('d-none');
        askBtn.disabled = true;
        questionInput.disabled = true;
        
        // Add user question to chat with animation
        showChatMessage(question, 'user');
        
        // Show typing indicator
        const typingIndicator = showTypingIndicator();
        
        // Clear input
        questionInput.value = '';
        
        try {
            const response = await fetch('/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question })
            });
            
            const data = await response.json();
            
            // Remove typing indicator after a minimum of 1 second for effect
            setTimeout(() => {
                if (typingIndicator && typingIndicator.parentNode) {
                    typingIndicator.parentNode.removeChild(typingIndicator);
                }
                
                if (response.ok) {
                    // Add bot response to chat with animation
                    showChatMessage(data.answer, 'bot');
                    
                    // Update remaining requests counter
                    if (data.remaining_requests !== undefined) {
                        updateRemainingRequestsUI(data.remaining_requests);
                    }
                } else {
                    if (data.limit_reached) {
                        // User has hit their request limit
                        showChatMessage('You have reached your limit of 10 questions. Please try again later.', 'bot');
                        updateRemainingRequestsUI(0);
                    } else {
                        showChatMessage(data.detail || 'Failed to get answer.', 'bot');
                    }
                }
            }, 1000);
        } catch (error) {
            console.error('Error:', error);
            
            // Remove typing indicator
            if (typingIndicator && typingIndicator.parentNode) {
                typingIndicator.parentNode.removeChild(typingIndicator);
            }
            
            showChatMessage('An error occurred while processing your question.', 'bot');
        } finally {
            // Make sure we re-enable input after a delay for the animation
            setTimeout(() => {
                // Hide spinner and enable button
                askSpinner.classList.add('d-none');
                askBtn.disabled = false;
                
                // Only re-enable if we still have requests left
                if (remainingRequests > 0) {
                    questionInput.disabled = false;
                    questionInput.focus();
                }
            }, 1000);
        }
    });

    // Function to display upload status
    function showUploadStatus(message, type) {
        uploadStatus.textContent = message;
        uploadStatus.className = `alert mt-3 alert-${type}`;
        uploadStatus.classList.remove('d-none');
        
        // Hide the status after 5 seconds
        setTimeout(() => {
            uploadStatus.classList.add('d-none');
        }, 5000);
    }

    // Function to display chat messages
    function showChatMessage(text, sender) {
        // Clear initial placeholder if this is the first message
        if (chatContainer.querySelector('.text-center')) {
            chatContainer.innerHTML = '';
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        // Create avatar
        const avatarDiv = document.createElement('div');
        avatarDiv.className = `chat-avatar ${sender}-avatar`;
        
        // Add appropriate icon
        const icon = document.createElement('i');
        icon.className = sender === 'bot' ? 'bi bi-robot' : 'bi bi-person';
        avatarDiv.appendChild(icon);
        
        // Create message content container
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Add message text
        const textP = document.createElement('p');
        textP.className = 'mb-0';
        textP.textContent = text;
        contentDiv.appendChild(textP);
        
        // Assemble the message
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        
        chatContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Function to display sample questions
    function displaySampleQuestions(questions, animated = false) {
        // Clear previous questions
        questionsList.innerHTML = '';
        
        // Add fade-in animation to the container
        sampleQuestions.classList.add('fade-in');
        
        // Add each question as a list item
        questions.forEach((question, index) => {
            const li = document.createElement('li');
            li.className = 'list-group-item list-group-item-action';
            
            // Add staggered animation if requested
            if (animated) {
                li.style.opacity = '0';
                li.style.transform = 'translateX(-10px)';
                li.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                
                // Delay each item appearance for staggered effect
                setTimeout(() => {
                    li.style.opacity = '1';
                    li.style.transform = 'translateX(0)';
                }, 100 * (index + 1));
            }
            
            li.textContent = question;
            
            // Add click event to use the question
            li.addEventListener('click', function() {
                questionInput.value = question;
                questionInput.focus();
                
                // Add pulse effect when clicked
                this.classList.add('pulse-animation');
                setTimeout(() => {
                    this.classList.remove('pulse-animation');
                }, 1000);
            });
            
            questionsList.appendChild(li);
        });
        
        // Show the sample questions section
        sampleQuestions.classList.remove('d-none');
        
        // Remove fade-in class after animation completes
        setTimeout(() => {
            sampleQuestions.classList.remove('fade-in');
        }, 500);
    }
    
    // Function to update visitor count
    async function updateVisitorCount() {
        try {
            const response = await fetch('/visitor-count');
            if (response.ok) {
                const data = await response.json();
                visitorCountElement.textContent = data.count;
            }
        } catch (error) {
            console.error('Error fetching visitor count:', error);
        }
    }
    
    // Function to check remaining requests
    async function checkRemainingRequests() {
        try {
            const response = await fetch('/remaining-requests');
            if (response.ok) {
                const data = await response.json();
                updateRemainingRequestsUI(data.remaining_requests);
            }
        } catch (error) {
            console.error('Error fetching remaining requests:', error);
        }
    }
    
    // Function to update the remaining requests UI
    function updateRemainingRequestsUI(count) {
        remainingRequests = count;
        
        // Update the counter in the UI
        if (requestLimitCounter) {
            requestLimitCounter.textContent = count;
            
            // Style counter based on remaining requests
            if (count <= 0) {
                requestLimitCounter.className = 'fw-bold request-limit-critical';
                showLimitReachedOverlay();
            } else if (count <= 2) {
                requestLimitCounter.className = 'fw-bold request-limit-low';
                // Add warning shake animation once
                if (!requestLimitCounter.dataset.warned) {
                    requestLimitCounter.classList.add('shake-animation');
                    setTimeout(() => {
                        requestLimitCounter.classList.remove('shake-animation');
                    }, 1000);
                    requestLimitCounter.dataset.warned = 'true';
                }
            } else {
                requestLimitCounter.className = 'fw-bold';
            }
            
            // Show the request limit container
            if (requestLimitContainer) {
                requestLimitContainer.classList.remove('d-none');
                
                // Add a fade-in animation if first display
                if (!requestLimitContainer.dataset.shown) {
                    requestLimitContainer.classList.add('fade-in');
                    requestLimitContainer.dataset.shown = 'true';
                }
            }
        }
        
        // If no requests left, disable all interactive elements
        if (count <= 0) {
            // Disable question input and button
            if (questionInput) questionInput.disabled = true;
            if (askBtn) askBtn.disabled = true;
            
            // Disable file upload
            if (uploadBtn) uploadBtn.disabled = true;
            const fileInput = document.getElementById('document-file');
            if (fileInput) fileInput.disabled = true;
            
            // Disable URL input
            if (urlBtn) urlBtn.disabled = true;
            const urlInput = document.getElementById('website-url');
            if (urlInput) urlInput.disabled = true;
            
            // Add a disabled appearance to the tab panels
            const tabPanels = document.querySelectorAll('.tab-pane');
            tabPanels.forEach(panel => {
                panel.classList.add('disabled-panel');
            });
        }
    }
    
    // Function to show an overlay when the limit is reached
    function showLimitReachedOverlay() {
        // Only show if we haven't already shown it
        if (document.querySelector('.limit-overlay')) return;
        
        const chatSection = document.querySelector('.card:nth-child(2)');
        if (!chatSection) return;
        
        // Create the overlay
        const overlay = document.createElement('div');
        overlay.className = 'limit-overlay';
        
        // Add content
        const icon = document.createElement('i');
        icon.className = 'bi bi-exclamation-triangle-fill limit-icon';
        
        const title = document.createElement('h3');
        title.className = 'text-danger mb-2';
        title.textContent = 'Limit Reached';
        
        const message = document.createElement('p');
        message.className = 'text-light text-center';
        message.textContent = 'You have reached your limit of 10 questions for today. Please try again tomorrow.';
        
        // Assemble the overlay
        overlay.appendChild(icon);
        overlay.appendChild(title);
        overlay.appendChild(message);
        
        // Add it to the chat card body
        const cardBody = chatSection.querySelector('.card-body');
        if (cardBody) {
            cardBody.style.position = 'relative';
            cardBody.appendChild(overlay);
        }
    }
    
    // Add typing indicator when bot is "thinking"
    function showTypingIndicator() {
        // Create typing indicator
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing-indicator-container';
        
        // Add bot avatar
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'chat-avatar bot-avatar';
        const icon = document.createElement('i');
        icon.className = 'bi bi-robot';
        avatarDiv.appendChild(icon);
        
        // Create indicator container
        const indicatorDiv = document.createElement('div');
        indicatorDiv.className = 'message-content';
        
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        
        // Add dots
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            typingIndicator.appendChild(dot);
        }
        
        indicatorDiv.appendChild(typingIndicator);
        
        // Assemble the message
        typingDiv.appendChild(avatarDiv);
        typingDiv.appendChild(indicatorDiv);
        
        // Add to chat container and scroll
        chatContainer.appendChild(typingDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        return typingDiv;
    }
});
