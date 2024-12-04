import React, { useState } from "react";
import JobDescriptionInput from "./components/JobDescriptionInput";
import CandidatesList from "./components/CandidatesList";
import Header from "./components/Header"; // Import the Header component

const App = () => {
  const [jobDescription, setJobDescription] = useState("");
  const [candidates, setCandidates] = useState([]);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmitDescription = () => {
    if (!jobDescription.trim()) {
      alert("Please enter a job description before submitting.");
      return;
    }
    setCandidates([
      { id: 1, title: "Candidate 1" },
      { id: 2, title: "Candidate 2" },
      { id: 3, title: "Candidate 3" },
      { id: 4, title: "Candidate 4" },
      { id: 5, title: "Candidate 5" },
    ]);
    setIsSubmitted(true);
  };

  const openChatPopup = (candidate) => {
    const popupWindow = window.open(
      "",
      "_blank",
      "width=400,height=600,scrollbars=yes,resizable=yes"
    );

    if (popupWindow) {
      popupWindow.document.write(`
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>Chat with ${candidate.title}</title>
          <style>
            body {
              font-family: Arial, sans-serif;
              margin: 0;
              padding: 10px;
              background-color: #f9f9f9;
            }
            .chat-header {
              background-color: #333;
              color: white;
              padding: 10px;
              text-align: center;
              font-size: 18px;
              font-weight: bold;
            }
            .chat-messages {
              height: 400px;
              overflow-y: auto;
              border: 1px solid #ccc;
              margin: 10px 0;
              padding: 10px;
              background-color: white;
            }
            .chat-input {
              display: flex;
              gap: 10px;
            }
            .chat-input input {
              flex: 1;
              padding: 8px;
              border: 1px solid #ccc;
              border-radius: 4px;
            }
            .chat-input button {
              padding: 8px 12px;
              border: none;
              background-color: #333;
              color: white;
              cursor: pointer;
              border-radius: 4px;
            }
          </style>
        </head>
        <body>
          <div class="chat-header">Chat with ${candidate.title}</div>
          <div id="chat-messages" class="chat-messages"></div>
          <div class="chat-input">
            <input id="chat-input" type="text" placeholder="Type your message..." />
            <button id="send-button">Send</button>
          </div>
          <script>
            const chatMessages = document.getElementById('chat-messages');
            const chatInput = document.getElementById('chat-input');
            const sendButton = document.getElementById('send-button');

            sendButton.addEventListener('click', () => {
              const userMessage = chatInput.value.trim();
              if (userMessage) {
                const userBubble = document.createElement('div');
                userBubble.textContent = "You: " + userMessage;
                userBubble.style.backgroundColor = "#faeabe";
                userBubble.style.padding = "10px";
                userBubble.style.marginBottom = "10px";
                userBubble.style.borderRadius = "10px";
                chatMessages.appendChild(userBubble);

                // Simulated bot response
                setTimeout(() => {
                  const botBubble = document.createElement('div');
                  botBubble.textContent = "Bot: Response to '" + userMessage + "'";
                  botBubble.style.backgroundColor = "#fffaed";
                  botBubble.style.padding = "10px";
                  botBubble.style.marginBottom = "10px";
                  botBubble.style.borderRadius = "10px";
                  chatMessages.appendChild(botBubble);
                }, 1000);

                chatInput.value = "";
              }
            });
          </script>
        </body>
        </html>
      `);
    } else {
      alert("Pop-up blocked! Please allow pop-ups for this site.");
    }
  };

  return (
    <div className="flex flex-col h-screen">
      <Header /> {/* Call the Header component */}
      <main className="flex flex-1">
        <div className="w-full p-4">
          <JobDescriptionInput
            setJobDescription={setJobDescription}
            onSubmit={handleSubmitDescription}
          />
          {isSubmitted && candidates.length > 0 && (
            <CandidatesList
              candidates={candidates}
              onShowCV={(candidate) => alert(`Showing CV for ${candidate.title}`)}
              onChat={openChatPopup}
            />
          )}
        </div>
      </main>
    </div>
  );
};

export default App;
