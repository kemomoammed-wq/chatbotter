// scripts.js: Client-side JavaScript for the advanced chatbot with all features
var socketio = io();
var typing = false;
var typingTimeout;

// Function to send a message
function sendMessage() {
    var messageInput = document.getElementById('message-input');
    var message = messageInput.value.trim();
    if (message) {
        socketio.emit('message', { message: message, image_data: null });
        messageInput.value = '';
    }
}

// Function to handle typing indicator
function handleTyping() {
    if (!typing) {
        typing = true;
        socketio.emit('typing');
        typingTimeout = setTimeout(() => {
            socketio.emit('stop_typing');
            typing = false;
        }, 2000);
    } else {
        clearTimeout(typingTimeout);
        typingTimeout = setTimeout(() => {
            socketio.emit('stop_typing');
            typing = false;
        }, 2000);
    }
}

// Function to add emoji to message
function addEmoji(emoji) {
    var messageInput = document.getElementById('message-input');
    messageInput.value += emoji;
    document.getElementById('emoji-picker').style.display = 'none';
}

// Function to toggle emoji picker
document.getElementById('emoji-btn').addEventListener('click', function() {
    var emojiPicker = document.getElementById('emoji-picker');
    emojiPicker.style.display = emojiPicker.style.display === 'block' ? 'none' : 'block';
});

// Function to upload image
function uploadImage(input) {
    var file = input.files[0];
    if (file && file.type.startsWith('image/')) {
        var reader = new FileReader();
        reader.onload = function(e) {
            var imageData = e.target.result;
            socketio.emit('upload', { file: imageData.split(',')[1], type: file.type });
        };
        reader.readAsDataURL(file);
    } else {
        alert('Please upload an image file.');
    }
    input.value = ''; // Clear file input
}

// Function to edit image with digital art style
function editImage() {
    var fileInput = document.getElementById('file-input');
    if (fileInput.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            socketio.emit('message', { message: 'edit image in digital art style', image_data: e.target.result });
        };
        reader.readAsDataURL(fileInput.files[0]);
    } else {
        alert('Please select an image first');
    }
}

// Function to translate message
function translateMessage() {
    var messageInput = document.getElementById('message-input');
    var message = messageInput.value.trim();
    if (message) {
        var targetLang = prompt('Enter target language code (e.g., "ar" for Arabic, "en" for English):');
        if (targetLang) {
            socketio.emit('message', { message: `translate to ${targetLang} ${message}`, image_data: null });
            messageInput.value = '';
        }
    } else {
        alert('Please enter a message to translate.');
    }
}

// Function to edit a message
function editMessage(msgId) {
    var newMessage = prompt('Edit your message:', document.getElementById(`msg-${msgId}`).querySelector('p').textContent);
    if (newMessage) {
        socketio.emit('edit_message', { msg_id: msgId, new_message: newMessage });
    }
}

// Function to add reaction
function addReaction(msgId, reaction) {
    socketio.emit('reaction', { msg_id: msgId, reaction: reaction });
}

// Function to create a chat item
function createChatItem(message, sender, id = null, reactions = {}, image_data = '', detected_lang = 'en') {
    var messages = document.getElementById("messages");
    var senderIsUser = "{{user}}" === sender;
    var reactionHtml = Object.entries(reactions).map(([react, users]) => `<span class="reaction">${react} (${users.length})</span>`).join('');
    var imageHtml = image_data ? `<img src="data:image/${image_data.split(';')[0].split('/')[1]};base64,${image_data}" style="max-width: 200px;"/>` : '';
    var langHtml = detected_lang !== 'en' ? `<small>Language: ${detected_lang}</small>` : '';
    var content = `
        <li id="msg-${id}" class="message-item ${senderIsUser ? "self-message-item" : "peer-message-item"} animate-new-msg">
            <p>${message}</p>
            ${imageHtml}
            ${langHtml}
            <small class="${senderIsUser ? "muted-text" : "muted-text-white"}">${new Date().toLocaleString()}</small>
            <div class="reactions">${reactionHtml}</div>
            ${senderIsUser ? `<button onclick="editMessage(${id})">Edit</button>` : ''}
            <button onclick="addReaction(${id}, '👍')">Like</button>
        </li>
    `;
    messages.innerHTML += content;
    messages.scrollTop = messages.scrollHeight;
}

// Socket event handlers
socketio.on('new_message', function(msg) {
    createChatItem(msg.message, msg.sender, msg.id, msg.reactions, msg.image_data || '', msg.detected_lang || 'en');
});

socketio.on('update_message', function(data) {
    var msg = document.getElementById(`msg-${data.msg_id}`);
    if (msg) msg.querySelector('p').textContent = data.message;
});

socketio.on('update_reaction', function(data) {
    var msg = document.getElementById(`msg-${data.msg_id}`);
    if (msg) {
        msg.querySelector('.reactions').innerHTML = Object.entries(data.reactions)
            .map(([react, users]) => `<span class="reaction">${react} (${users.length})</span>`).join('');
    }
});

socketio.on('update_online', function(count) {
    document.getElementById('online-count').textContent = `Online: ${count}`;
});

socketio.on('typing', function(users) {
    var indicator = document.getElementById('typing-indicator');
    indicator.textContent = users.length ? `${users.join(', ')} is typing...` : '';
});

socketio.on('connect', function() {
    console.log('Connected to server');
});

socketio.on('disconnect', function() {
    console.log('Disconnected from server');
});

// Event listeners
document.getElementById('message-input').addEventListener('input', handleTyping);
document.getElementById('send-btn').addEventListener('click', sendMessage);
document.getElementById('file-input').addEventListener('change', uploadImage);
document.getElementById('edit-image-btn').addEventListener('click', editImage);
document.getElementById('translate-btn').addEventListener('click', translateMessage);

// Dark mode toggle
document.getElementById('dark-mode-toggle').addEventListener('click', function() {
    document.body.classList.toggle('dark-mode');
});

// Language toggle (basic switch between RTL/LTR)
document.getElementById('lang-toggle').addEventListener('click', function() {
    var container = document.getElementById('room-container');
    container.dir = container.dir === 'ltr' ? 'rtl' : 'ltr';
    document.getElementById('message-input').placeholder = container.dir === 'rtl' ? 'أدخل رسالتك' : 'Enter your message';
});

// Voice input (basic placeholder)
document.getElementById('voice-btn').addEventListener('click', function() {
    alert('Voice input feature is under development.');
});