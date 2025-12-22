// ============================================================
// MUET Chatbot - JavaScript
// ============================================================

const API_URL = window.location.origin;

// DOM Elements
const chatbotContainer = document.getElementById('chatbotContainer');
const chatbotToggle = document.getElementById('chatbotToggle');
const toggleIcon = document.getElementById('toggleIcon');
const notificationBadge = document.getElementById('notificationBadge');
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const quickSuggestions = document.getElementById('quickSuggestions');
const resizeHandle = document.getElementById('resizeHandle');

// State
let isOpen = false;
let isFirstOpen = true;
let isResizing = false;

// ============================================================
// Resize Functionality (from top-left corner)
// ============================================================
resizeHandle.addEventListener('mousedown', initResize);

function initResize(e) {
    isResizing = true;
    
    const startX = e.clientX;
    const startY = e.clientY;
    const startWidth = chatbotContainer.offsetWidth;
    const startHeight = chatbotContainer.offsetHeight;
    const startBottom = parseInt(window.getComputedStyle(chatbotContainer).bottom);
    const startRight = parseInt(window.getComputedStyle(chatbotContainer).right);
    
    function doResize(e) {
        if (!isResizing) return;
        
        const deltaX = startX - e.clientX;
        const deltaY = startY - e.clientY;
        
        const newWidth = Math.min(Math.max(startWidth + deltaX, 280), 600);
        const newHeight = Math.min(Math.max(startHeight + deltaY, 350), window.innerHeight * 0.8);
        
        chatbotContainer.style.width = newWidth + 'px';
        chatbotContainer.style.height = newHeight + 'px';
    }
    
    function stopResize() {
        isResizing = false;
        document.removeEventListener('mousemove', doResize);
        document.removeEventListener('mouseup', stopResize);
    }
    
    document.addEventListener('mousemove', doResize);
    document.addEventListener('mouseup', stopResize);
    
    e.preventDefault();
}

// ============================================================
// Toggle Chatbot
// ============================================================
function toggleChatbot() {
    isOpen = !isOpen;
    
    if (isOpen) {
        chatbotContainer.classList.add('active');
        toggleIcon.classList.remove('fa-comments');
        toggleIcon.classList.add('fa-times');
        notificationBadge.style.display = 'none';
        userInput.focus();
        
        if (isFirstOpen) {
            isFirstOpen = false;
        }
    } else {
        chatbotContainer.classList.remove('active');
        toggleIcon.classList.remove('fa-times');
        toggleIcon.classList.add('fa-comments');
    }
}

// ============================================================
// Send Message
// ============================================================
async function sendMessage() {
    const message = userInput.value.trim();
    
    if (!message) return;
    
    // Clear input
    userInput.value = '';
    
    // Hide quick suggestions after first message
    quickSuggestions.style.display = 'none';
    
    // Add user message
    addMessage(message, 'user');
    
    // Show typing indicator
    const typingId = showTypingIndicator();
    
    // Disable send button
    sendBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: message })
        });
        
        // Remove typing indicator
        removeTypingIndicator(typingId);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to get response');
        }
        
        const data = await response.json();
        addMessage(data.answer, 'bot');
        
    } catch (error) {
        console.error('Error:', error);
        removeTypingIndicator(typingId);
        addMessage(`Sorry, I encountered an error: ${error.message}. Please try again.`, 'bot', true);
    } finally {
        sendBtn.disabled = false;
        userInput.focus();
    }
}

// ============================================================
// Send Suggestion
// ============================================================
function sendSuggestion(text) {
    userInput.value = text;
    sendMessage();
}

// ============================================================
// Add Message to Chat
// ============================================================
function addMessage(text, sender, isError = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message${isError ? ' error-message' : ''}`;
    
    const avatarIcon = sender === 'bot' ? 'fa-robot' : 'fa-user';
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas ${avatarIcon}"></i>
        </div>
        <div class="message-content">
            <p>${formatMessage(text)}</p>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// ============================================================
// Format Message (handle newlines, links, etc.)
// ============================================================
function formatMessage(text) {
    // Escape HTML
    text = text.replace(/&/g, '&amp;')
               .replace(/</g, '&lt;')
               .replace(/>/g, '&gt;');
    
    // Convert newlines to <br>
    text = text.replace(/\n/g, '<br>');
    
    // Convert URLs to links
    text = text.replace(
        /(https?:\/\/[^\s<]+)/g,
        '<a href="$1" target="_blank" rel="noopener noreferrer" style="color: #0066cc; text-decoration: underline;">$1</a>'
    );
    
    // Convert markdown bold (**text**)
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convert markdown italic (*text*)
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    return text;
}

// ============================================================
// Typing Indicator
// ============================================================
function showTypingIndicator() {
    const id = 'typing-' + Date.now();
    const typingDiv = document.createElement('div');
    typingDiv.id = id;
    typingDiv.className = 'message bot-message';
    typingDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(typingDiv);
    scrollToBottom();
    
    return id;
}

function removeTypingIndicator(id) {
    const typingDiv = document.getElementById(id);
    if (typingDiv) {
        typingDiv.remove();
    }
}

// ============================================================
// Scroll to Bottom
// ============================================================
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// ============================================================
// Clear Chat
// ============================================================
function clearChat() {
    // Keep only the welcome message
    const messages = chatMessages.querySelectorAll('.message');
    messages.forEach((msg, index) => {
        if (index > 0) {
            msg.remove();
        }
    });
    
    // Show quick suggestions again
    quickSuggestions.style.display = 'flex';
}

// ============================================================
// Handle Enter Key
// ============================================================
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// ============================================================
// Check API Health on Load
// ============================================================
async function checkApiHealth() {
    try {
        const response = await fetch(`${API_URL}/health`);
        const data = await response.json();
        
        if (!data.qa_chain_ready) {
            console.warn('QA Chain is not ready yet');
        }
    } catch (error) {
        console.error('API health check failed:', error);
    }
}

// ============================================================
// Initialize
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    checkApiHealth();
    
    // Show notification badge after 3 seconds
    setTimeout(() => {
        if (!isOpen) {
            notificationBadge.style.display = 'flex';
        }
    }, 3000);
});
