import React, { useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../style.css';
import { TypeAnimation } from 'react-type-animation';

function PageTwo() {
    const text04Ref = useRef(null);
    const text07Ref = useRef(null);
    const buttons01Ref = useRef(null);
    const text07_2Ref = useRef(null);
    const text04DuplicateRef = useRef(null);
    const navigate = useNavigate();

    useEffect(() => {
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

    useEffect(() => {
        const timer = setTimeout(() => {
            navigate('/page-three');
        }, 3000); // 7 seconds

        return () => clearTimeout(timer);
    }, [navigate]);

    return (
        <div id="wrapper" className="page-two">
            <div
                id="main-wrapper"
                style={{
                    position: 'relative',
                    textAlign: 'center',
                    paddingTop: '140px',
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
                        <div
                            style={{
                                width: '70px',
                                height: '70px',
                                margin: '20px auto',
                                border: '4px solid rgba(255, 255, 255, 0.1)',
                                borderTop: '4px solid rgba(140, 158, 114, 0.75)',
                                borderRadius: '50%',
                                animation: 'spin 1s linear infinite',
                            }}
                        />
                        {/* Other content can remain the same */}
                    </div>
                </div>
                <h1
                    id="text04_2"
                    ref={text04DuplicateRef}
                    className="fade-right"
                >
                    <span style={{ fontSize: '0.5em' }}>
                        ...analyzing your mystery pill:<br />
                    </span>
                    <TypeAnimation
                        sequence={[
                            'advil', 280, 'advil?', 600, '', 280,
                            'paracetamol', 280, 'paracetamol?', 600, '', 280,
                            'xanax', 280, 'xanax?', 600, '',
                        ]}
                        wrapper="span"
                        cursor={false}
                        repeat={Infinity}
                        className="custom-cursor"
                        style={{
                            display: 'inline-block',
                            color: 'rgba(140, 158, 114, 0.75)',
                            fontSize: '0.5em',
                        }}
                    />
                    {/* Remove the manual navigation button */}
                </h1>
            </div>
        </div>
    );
}

export default PageTwo;