import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import './style.css';
import PageOne from './components/PageOne';
import PageTwo from './components/PageTwo';
import PageThree from './components/PageThree';
import PageFour from './components/PageFour';
import Header from './components/Header';
import ImageContext from './components/ImageContext'; // Import the context

function App() {
    const [uploadedImage, setUploadedImage] = useState(null);

    useEffect(() => {
        // Redirect to PageOne on page refresh for non-root paths
        if (window.location.pathname !== '/') {
            window.location.replace('/');
        }
    }, []);

    return (
        <ImageContext.Provider value={{ uploadedImage, setUploadedImage }}>
            <Router>
                <div>
                    <Header />
                    <Routes>
                        <Route path="/" element={<PageOne />} />
                        <Route path="/page-two" element={<PageTwo />} />
                        <Route path="/page-three" element={<PageThree />} />
                        <Route path="/page-four" element={<PageFour />} />
                    </Routes>
                </div>
            </Router>
        </ImageContext.Provider>
    );
}

export default App;
