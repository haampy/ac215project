import React, { useRef, useContext, useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FaCommentDots } from 'react-icons/fa'; // Import chat icon from react-icons
import '../style.css';
import noImage from '../images/sample_uploaded_pill/nothing.png';
import ImageContext from './ImageContext'; // Import the context

function PageThree() {
    const text04Ref = useRef(null);
    const text07Ref = useRef(null);
    const buttons01Ref = useRef(null);
    const text07_2Ref = useRef(null);
    const text04DuplicateRef = useRef(null);
    const imageRef = useRef(null);
    const [imageBottom, setImageBottom] = useState(0);
    const { uploadedImage } = useContext(ImageContext);

    // Matches array
    const matches = [
        "Benadryl",
        "Definitely Benadryl",
        "Advil",
        "Definitely Benadryl",
        "Advil",
        "Definitely Benadryl",
        "Advil",
        "Advil",
        "Advil",
    ];

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
                    top: '100px', // Keep the image in its current position
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
                    top: `${imageBottom}px`, // Start the gray box directly below the image with a gap
                    left: 0,
                    width: '100%',
                }}
            >
                <div id="main">
                    <div className="inner">
                        <h1
                            id="text04"
                            ref={text04Ref}
                            className="fade-right"
                            style={{ marginTop: '-10px', marginBottom: '-40px' }}
                        >
                            __________________
                        </h1>
                        <p
                            id="text07"
                            ref={text07Ref}
                            style={{
                                marginTop: '-10px',
                                marginBottom: '20px',
                                fontSize: '1.2rem',
                                textAlign: 'center',
                            }}
                            className="fade-in"
                        >
                            Possible Matches
                        </p>
                        {/* Dynamically render matches */}
                        {matches.map((match, index) => (
    <div className="transparent-box" key={index} style={{ position: 'relative' }}>
        <div>{match}</div>
        <div
            style={{
                fontSize: '0.7rem',
                marginTop: '0.5rem',
                color: 'rgba(255, 255, 255, 0.6)',
                marginBottom: '1rem',
            }}
        >
            Other names:
        </div>
        <div
            style={{
                position: 'absolute',
                top: '50%',
                transform: 'translateY(-50%)',
                right: '10px',
            }}
        >
            {/* Wrap the chat icon with Link and pass the match via state */}
            <Link to="/page-four" state={{ selectedMatch: match }}>
                <FaCommentDots
                    style={{
                        color: 'rgba(255, 255, 255, 0.8)',
                        fontSize: '1rem',
                    }}
                />
            </Link>
        </div>
        {/* Keep the line directly below the chat icon */}
        <div className="box-line"></div>
    </div>
))}
                        {/* Move the button here */}
                        <ul
                            id="buttons01"
                            className="buttons fade-down"
                            ref={buttons01Ref}
                            style={{ marginTop: '20px', textAlign: 'center' }} // Ensure it aligns properly
                        >
                            <li>
                                <Link
                                    to="/page-four"
                                    className="button n01"
                                    style={{
                                        padding: '0.4rem 0.8rem',
                                        fontSize: '0.8rem',
                                        width: 'auto',
                                        backgroundColor: 'rgba(128, 128, 128, 0.1)',
                                    }}
                                >
                                    <span
                                        className="label"
                                        style={{
                                            fontSize: '0.8rem',
                                        }}
                                    >
                                        Go to page 4
                                    </span>
                                </Link>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default PageThree;
