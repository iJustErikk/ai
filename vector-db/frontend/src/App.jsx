import React, { useState, useEffect } from 'react';
import { FileUploader } from "react-drag-drop-files";
import './App.css';
import defaultImage from "./assets/default.jpeg";

// HACK for codespaces demo
const ip = window.location.href.split('//')[1].split('/')[0];
const port = ip.includes('github') ? '' : 8000;

function App() {
  const [selectedImage, setSelectedImage] = useState(defaultImage);
  const [searchResults, setSearchResults] = useState([]);
  const [selectedImageSrc, setSelectedImageSrc] = useState(defaultImage);

  useEffect(() => {
    if (selectedImage == defaultImage) return;
    const reader = new FileReader();
    reader.onload = () => {
        const srcData = reader.result;
        setSelectedImageSrc(srcData);
    };
    reader.readAsDataURL(selectedImage);
  }, [selectedImage]);

  const handleUpload = async (event) => {
    event.preventDefault();

    if (!selectedImage) {
      alert('Please select an image to upload');
      return;
    }
    
    const formData = new FormData();
    if (selectedImage === defaultImage) {
      const response = await fetch(defaultImage);
      const imgBlob = await response.blob();
  
      formData.append("image", imgBlob, "default.jpeg");
    } else {
      formData.append("image", selectedImage);
    }

    try {
      const response = await fetch(`https://${ip}:${port}/upload-image`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();
      alert('Upload success');
    } catch (error) {
      alert('Upload failed');
    }
  };

  const handleSearch = async (event) => {
    event.preventDefault();

    if (!selectedImage) {
      alert('Please select an image to search');
      return;
    }

    const formData = new FormData();
    if (selectedImage === defaultImage) {
      const response = await fetch(defaultImage);
      const imgBlob = await response.blob();
  
      formData.append("image", imgBlob, "default.jpeg");
    } else {
      formData.append("image", selectedImage);
    }

    try {
      console.log(`https://${ip}:${port}/search-image`)
      const response = await fetch(`https://${ip}:${port}/search-image`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data = await response.json();
      setSearchResults(data.results);
    } catch (error) {
      alert("search failed");
    }
  };

  return (
    <div className="App">
      <h1>Reverse Image Search</h1>        
      <img className='selected-image' src={selectedImageSrc} alt="selected image"/>
      <p>Selected Image</p>
      <FileUploader handleChange={setSelectedImage} name="file" types={['png', 'jpg', 'jpeg']} />
      <div style = {{ marginTop : 20 }}>
      <button onClick={handleUpload}>Upload</button>
      <button onClick={handleSearch}>Search</button>
      </div>
      {searchResults.length ? <h2>Most Similar Images:</h2> : ""}
      <div className="image-grid">
        {searchResults.map((result) => (
          <div key={result.id}>
            <img src={`https://${ip}:${port}/${result.path}`} alt={result.name} />
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
