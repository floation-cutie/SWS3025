import React from 'react';
import { useNavigate } from 'react-router-dom';

const NotFoundPage = () => {
  const navigate = useNavigate();

  return (
    <div className="h-screen flex flex-col justify-center items-center bg-gray-50">
      <h1 className="text-6xl font-bold text-gray-800">404</h1>
      <p className="text-xl font-semibold text-gray-600 mt-2">Not Found</p>
      <p className="text-md text-gray-500 mt-2">The page you are looking for does not exist</p>
      <button 
        onClick={() => navigate('/')}
        className="mt-6 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-700 transition duration-300 ease-in-out"
      >
        Go back to homepage
      </button>
    </div>
  );
};

export default NotFoundPage;
