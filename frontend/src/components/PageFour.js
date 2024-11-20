import React, { useRef, useContext, useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom'; // Import useLocation
import { FaCommentDots, FaPaperPlane } from 'react-icons/fa'; // FaPaperPlane for the send icon
import { BiSolidSend } from "react-icons/bi";
import { PiArrowCircleUpThin } from "react-icons/pi";
import '../style.css';
import noImage from '../images/sample_uploaded_pill/nothing.png';
import ImageContext from './ImageContext';

function PageFour() {
    const text04Ref = useRef(null);
    const text07Ref = useRef(null);
    const buttons01Ref = useRef(null);
    const text07_2Ref = useRef(null);
    const text04DuplicateRef = useRef(null);
    const imageRef = useRef(null);
    const chatContainerRef = useRef(null); // Ref for the chat container
    const [imageBottom, setImageBottom] = useState(0);
    const { uploadedImage } = useContext(ImageContext);

    // Use useLocation to get the state passed via Link
    const location = useLocation();
    const { selectedMatch } = location.state || {};

    // Set the selected array to use the selectedMatch or default to "Benadryl"
    const selected = [selectedMatch || "Benadryl"];

    // Chat state
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');

    const handleSendMessage = () => {
        if (inputValue.trim() === '') return;

        // Add user's message
        const userMessage = { sender: 'user', text: inputValue };

        // Add bot's reply (exact copy)
        const botMessage = { sender: 'bot', text: inputValue };

        setMessages([...messages, userMessage, botMessage]);

        setInputValue('');
    };

    // Automatically scroll to the bottom of the chat when messages update
    useEffect(() => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTo({
                top: chatContainerRef.current.scrollHeight,
                behavior: 'smooth', // Smooth scrolling
            });
        }
    }, [messages]);

    // Calculate the bottom position of the image dynamically
    useEffect(() => {
        if (imageRef.current) {
            const updateImageBottom = () => {
                const rect = imageRef.current.getBoundingClientRect();
                setImageBottom(rect.bottom + window.scrollY + 20); // Add a consistent gap (20px here)
            };

            updateImageBottom();

            // Recalculate if the window resizes
            window.addEventListener('resize', updateImageBottom);
            return () => window.removeEventListener('resize', updateImageBottom);
        }
    }, []);

    React.useEffect(() => {
        const options = { threshold: 0.25 };
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, options);

        const elements = [
            text04Ref.current,
            text07Ref.current,
            buttons01Ref.current,
            text07_2Ref.current,
            text04DuplicateRef.current,
        ];

        elements.forEach((el) => el && observer.observe(el));

        return () => {
            elements.forEach((el) => el && observer.unobserve(el));
        };
    }, []);

    return (
        <div id="wrapper" style={{ position: 'relative' }}>
            {/* Static image container */}
            <div
                style={{
                    position: 'absolute',
                    top: '100px',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    textAlign: 'center',
                }}
            >
                <img
                    ref={imageRef}
                    src={uploadedImage || noImage}
                    alt="Uploaded pill"
                    style={{
                        width: '150px',
                        height: 'auto',
                        borderRadius: '8px',
                    }}
                />
            </div>

            {/* Main content starts here */}
            <div
                id="main-wrapper"
                style={{
                    position: 'absolute',
                    top: `${imageBottom}px`,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    display: 'flex',
                    flexDirection: 'column',
                }}
            >
                <div
                    id="main"
                    style={{ flex: 1, display: 'flex', flexDirection: 'column' }}
                >
                    <div
                        className="inner"
                        style={{ flex: 1, display: 'flex', flexDirection: 'column' }}
                    >
                        <h1
                            id="text04"
                            ref={text04Ref}
                            className="fade-right"
                            style={{ marginTop: '-10px', marginBottom: '-40px' }}
                        >
                            __________________
                        </h1>
                        <div
                            style={{
                                backgroundColor: 'rgba(50, 50, 50, 0.8)',
                                position: 'fixed',
                                top: 0,
                                left: 0,
                                right: 0,
                                zIndex: 999,
                                padding: '10px 0',
                                backdropFilter: 'blur(4px)',
                            }}
                        >
                            <p
                                id="text07"
                                ref={text07Ref}
                                style={{
                                    margin: '0',
                                    fontSize: '1.2rem',
                                    textAlign: 'center',
                                    color: 'white',
                                }}
                                className="fade-in"
                            >
                                PillRx Chat: {selected[0]}
                            </p>
                        </div>
                        {/* Chat interface inside the transparent box */}
                        <div
                            className="transparent-box"
                            style={{
                                padding: '20px',
                                display: 'flex',
                                flexDirection: 'column',
                                flex: 1,
                            }}
                        >
                            {/* Messages area */}
                            <div
                                className="chat-container"
                                ref={chatContainerRef}
                                style={{
                                    flex: 1,
                                    overflowY: 'auto',
                                    marginBottom: '10px',
                                    paddingRight: '10px',
                                    marginTop: '-30px',
                                    zIndex: 998,
                                }}
                            >
                                {messages.map((message, index) => (
                                    <div
                                        key={index}
                                        style={{
                                            display: 'flex',
                                            justifyContent:
                                                message.sender === 'user' ? 'flex-end' : 'flex-start',
                                            position: 'relative',
                                        }}
                                    >
                                        <div
                                            className={`message ${message.sender === 'bot' ? 'bot' : ''}`}
                                            style={{
                                                backgroundColor:
                                                    message.sender === 'user'
                                                        ? 'rgba(140, 158, 114, 0.5)'
                                                        : 'transparent',
                                                color: message.sender === 'user' ? 'white' : 'white',
                                                borderRadius: '15px',
                                                padding: '10px',
                                                margin: '5px',
                                                maxWidth: message.sender === 'bot' ? '100%' : '80%',
                                                wordBreak: 'break-word',
                                                whiteSpace: 'pre-wrap',
                                            }}
                                        >
                                            {message.text}
                                        </div>
                                    </div>
                                ))}
                            </div>
                            {/* Input area */}
                            <div
                                className="input-container"
                                style={{ display: 'flex', paddingLeft: '15px' }}
                            >
                                <input
                                    type="text"
                                    placeholder="Type your message..."
                                    value={inputValue}
                                    onChange={(e) => setInputValue(e.target.value)}
                                    onKeyPress={(e) => {
                                        if (e.key === 'Enter') {
                                            handleSendMessage();
                                        }
                                    }}
                                    style={{
                                        flex: 1,
                                        padding: '10px',
                                        borderRadius: '20px',
                                        backgroundColor: 'transparent',
                                        border: '1px solid rgba(150, 150, 150, 0.7)',
                                        marginRight: '10px',
                                        color: 'white',
                                    }}
                                />
                                <button
                                    onClick={handleSendMessage}
                                    style={{
                                        backgroundColor: 'transparent',
                                        border: 'none',
                                        padding: '0',
                                        margin: '0',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                    }}
                                >
                                    <PiArrowCircleUpThin
                                        style={{
                                            fontSize: '2.5rem',
                                            color: 'rgba(140, 158, 114, 0.78)',
                                        }}
                                    />
                                </button>
                            </div>
                        </div>
                        {/* End of chat interface */}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default PageFour;
