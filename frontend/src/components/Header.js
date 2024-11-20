import React from 'react';
import pillImage from '../images/pills/white_transparent.png';
import '../style.css';
import { Link } from 'react-router-dom';

function Header() {
    return (
        <div
            id="header"
            style={{
                display: 'flex',
                alignItems: 'center',
                position: 'absolute',
                top: '1rem',
                left: '1rem',
                gap: '0.5rem',
            }}
        >
            <Link to="/">
            <img
                src={pillImage}
                alt="Pill Icon"
                style={{
                    width: '30px',
                    height: '25px',
                }}
            />
            </Link>
            <Link to="/" style={{ textDecoration: 'none' }}>
            <span
                id="text02"
                style={{
                    color: '#8C9E72',
                    fontFamily: 'Sora, sans-serif',
                    letterSpacing: '0.225rem',
                    fontSize: '0.75em',
                    fontWeight: '600',
                    textTransform: 'uppercase',
                }}
            >
                PILLRX
            </span>
            </Link>
        </div>
    );
}

export default Header;