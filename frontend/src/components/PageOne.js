import React, { useRef, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import '../style.css';
import pillImage from '../images/uploading/1_white.png';
import { TypeAnimation } from 'react-type-animation';
import ImageContext from './ImageContext';

function PageOne() {
    const text04Ref = useRef(null);
    const text07Ref = useRef(null);
    const buttons01Ref = useRef(null);
    const text07_2Ref = useRef(null);
    const text04DuplicateRef = useRef(null);
    const navigate = useNavigate();
    const { setUploadedImage } = useContext(ImageContext);

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

    const handleDragOver = (event) => {
        event.preventDefault();
        event.stopPropagation();
    };

    const handleDrop = (event) => {
        event.preventDefault();
        event.stopPropagation();
        const files = event.dataTransfer.files;
        if (files && files.length > 0) {
            const file = files[0];
            const reader = new FileReader();
            reader.onload = (e) => {
                const dataURL = e.target.result;
                setUploadedImage(dataURL);
                navigate('/page-two');
            };
            reader.readAsDataURL(file);
            event.dataTransfer.clearData();
        }
    };

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const dataURL = e.target.result;
                setUploadedImage(dataURL);
                navigate('/page-two');
            };
            reader.readAsDataURL(file);
        }
    };

    return (
        <div id="wrapper">
            <div
                id="main-wrapper"
                style={{
                    position: 'relative',
                    textAlign: 'center',
                    paddingTop: '140px',
                    width: '100%',
                }}
            >
                <h1
                    id="text04_2"
                    ref={text04DuplicateRef}
                    className="fade-right"
                    style={{
                        position: 'absolute',
                        top: '-40px',
                        left: '50%',
                        transform: 'translateX(-50%)',
                    }}
                >
                    Can I take my pill with{' '}
                    <TypeAnimation
                        sequence={[
                            'alcohol', 280, 'alcohol?', 1300, '', 280,
                            'paracetamol', 500, 'paracetamol?', 1300, '', 280,
                            'xanax', 500, 'xanax?', 1300, '', 500,
                        ]}
                        wrapper="span"
                        cursor={false}
                        repeat={Infinity}
                        className="custom-cursor"
                        style={{
                            display: 'inline-block',
                            color: 'rgba(140, 158, 114, 0.75)',
                        }}
                    />
                </h1>
                {/* Attach drag-and-drop handlers to the outermost container */}
                <div
                    id="main"
                    onDragOver={handleDragOver}
                    onDrop={handleDrop}
                    style={{
                        border: '0.25px solid rgba(255, 255, 255, 0.2)', // Changed to a smooth, thinner border
                        borderRadius: '8px',
                        padding: '20px',
                        // backgroundColor: 'rgba(255, 255, 255, 0.05)', // Optional gray background
                    }}
                >
                    <div className="inner">
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
                                display: 'block',
                                margin: '20px auto',
                                width: '70px',
                                height: '70px',
                                position: 'relative',
                            }}
                        >
                            <img
                                src={pillImage}
                                alt="Upload your pill"
                                style={{
                                    width: '100%',
                                    height: '100%',
                                    objectFit: 'contain',
                                }}
                            />
                        </div>
                        <p
                            id="text07"
                            ref={text07Ref}
                            style={{
                                marginTop: '3px',
                                marginBottom: '20px',
                                fontSize: '1.2rem',
                            }}
                            className="fade-in"
                        >
                            Drop your pill image here or:
                        </p>
                        <ul
    id="buttons01"
    className="buttons fade-down"
    ref={buttons01Ref}
>
    <li>
        {/* Replacing Link with file input */}
        <label
            className="button n01"
            style={{
                cursor: 'pointer',
                color: 'rgba(255, 255, 255, 0.8)', // Match the color of "PillRx"
                backgroundColor: 'rgba(140, 158, 114, 0.75)', // Optional: adjust background if needed
                // border: '1px solid rgba(140, 158, 114, 0.75)', // Border to make it stand out
                padding: '10px 20px',
                borderRadius: '4px',
                textAlign: 'center',
                display: 'inline-block',
            }}
        >
            <span className="label">Browse File</span>
            <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                style={{
                    display: 'none', // Hide the default input
                }}
            />
        </label>
    </li>
</ul>

                        <p
                            id="text07_2"
                            ref={text07_2Ref}
                            style={{
                                marginTop: '20px',
                                fontSize: '0.65rem',
                            }}
                            className="fade-in"
                        >
                            Supports: JPEG, PNG
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default PageOne;