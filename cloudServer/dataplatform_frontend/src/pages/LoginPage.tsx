import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Cookies from 'js-cookie';
import videoBackground from '../Videos/4.mp4'; // 引入视频文件

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      const response = await fetch('http://192.168.92.45:5000/api/users/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });
      const data = await response.json();

      if (response.ok) {
        Cookies.set('token', data.token, { expires: 7 });
        navigate('/dashboard');
      } else {
        alert(data.msg);
      }
    } catch (error) {
      console.error('Login failed', error);
    }
  };

  return (
    <div className="flex min-h-screen relative">
      <video autoPlay loop muted className="absolute w-full h-full object-cover">
        <source src={videoBackground} type="video/mp4" />
      </video>
      
      <div className="absolute w-full h-full bg-black opacity-10"></div>

      <div className="w-full flex justify-center items-center z-10">
        <div className="bg-white shadow-lg rounded-lg p-5 max-w-md w-full opacity-85">
          <div>
            <img src="/src/pics/logo.svg" alt="logo" className="w-20 h-20 mx-auto" />
            <p className="text-center text-2xl font-extrabold text-gray-900">Smart White Cane</p>
          </div>
          <h2 className="text-center text-3xl font-extrabold text-gray-900 mt-2">
            Log in to your account
          </h2>
          <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="email" className="sr-only">Email</label>
              <input id="email" name="email" type="email" autoComplete="email" required 
                    className="appearance-none rounded-none relative block w-full px-4 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm" 
                    placeholder="Email" value={email} 
                    onChange={e => setEmail(e.target.value)} />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">Password</label>
              <input id="password" name="password" type="password" autoComplete="current-password" required 
                     className="appearance-none rounded-none relative block w-full px-4 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                     placeholder="Password" value={password} 
                     onChange={e => setPassword(e.target.value)} />
            </div>
            <div>
              <button type="submit" className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                Log in
              </button>
            </div>
          </form>
          <p className="mt-2 text-center text-sm text-gray-600">
            Don't have an account?{' '}
            <a href="#" onClick={() => navigate('/register')} className="font-medium text-indigo-600 hover:text-indigo-500">
              Register
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
