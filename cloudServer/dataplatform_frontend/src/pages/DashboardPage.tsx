import React, { useState, useEffect } from 'react';
import Modal from 'react-modal';
import io from 'socket.io-client';
import UserProfileDropdown from '../components/UserProfileDropdown';
import DataInfo from '../components/DataInfo';
import VideoMonitor from '../components/VideoMonitor';
import MapLocation from '../components/MapLocation';

Modal.setAppElement('#root');

export default function Dashboard() {
  const [modalIsOpen, setModalIsOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [modalType, setModalType] = useState('message');  // Default to message

  useEffect(() => {
    const socket = io('http://192.168.92.51:8008');  // 确保这个地址与 Flask 后端一致

    socket.on('connect', () => {
      console.log('Connected to the server.');
    });

    socket.on('alert', data => {
      setMessage(data.message);
      setModalType(data.type);  // Could be 'input' or 'message'
      setModalIsOpen(true);
    });

    socket.on('disconnect', () => {
      console.log('Disconnected from the server.');
    });

    return () => {
      socket.close();
    };
  }, []);

  const handleSubmit = () => {
    const socket = io('http://192.168.92.51:8008');
    socket.emit('response_from_client', { response });
    setModalIsOpen(false); // 关闭模态框
  };

  const handleCloseModal = () => {
    setModalIsOpen(false);
  }

  return (
    <div className="bg-gray-100 min-h-screen p-5">
      <Modal
        isOpen={modalIsOpen}
        onRequestClose={() => setModalIsOpen(false)}
        className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center"
        overlayClassName="fixed inset-0 bg-black bg-opacity-50"
      >
        <div className="w-[500px] bg-white p-6 rounded-lg shadow-xl max-w-sm mx-auto">
          <h2 className="text-xl font-bold mb-4">Alert</h2>
          <p className="break-words whitespace-pre-wrap">{message}</p>
          {modalType === 'input' && (
            <form onSubmit={handleSubmit} className="space-y-4 mt-5">
              <input
                type="text"
                value={response}
                onChange={e => setResponse(e.target.value)}
                placeholder="Type your response"
                className="w-full p-2 border border-gray-300 rounded"
              />
              <button type="submit" className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600">
                Submit
              </button>
            </form>
          )}
          {modalType === 'message' && (
              <button onClick={handleCloseModal} className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600 mt-5">
                Close
              </button>
            )
          }
        </div>
      </Modal>
      <div className="max-w-6xl mx-auto">
      <header className="w-[1000px] flex flex-col justify-between items-start mb-10 mt-10 mx-auto">
        <div className="flex justify-between items-center w-full">
          <div className="flex items-center">
            <img src="/src/pics/logo.svg" alt="logo" className="h-20" />
            <h1 className="text-4xl font-bold">Smart White Cane Dashboard</h1>
          </div>
          <UserProfileDropdown />
        </div>
      </header>
      <div className="w-[1000px] h-[620px] flex justify-between gap-5 mx-auto">
        <DataInfo />
        <VideoMonitor />
      </div>
      <div className="w-[1000px] mt-10 mx-auto">
        <MapLocation />
      </div>
      <footer className="w-full mt-10 text-center flex items-center justify-center">
        <img src="/src/pics/nus.png" alt="nuslogo" className="h-20 mr-4" />
        <p className="text-sm">
          &copy; 2024 SWS3025 Group 8
        </p>
      </footer>
    </div>
    </div>
  );
}
