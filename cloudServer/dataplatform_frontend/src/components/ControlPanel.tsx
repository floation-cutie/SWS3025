import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowUp, faSearchPlus, faSearchMinus } from '@fortawesome/free-solid-svg-icons';
import './circle.css';

const Circle = () => {
    const sectors = [];

    const handleSectorClick = (index) => {
        console.log(`Sector ${index} clicked`);
    };

    for (let i = 0; i < 8; i++) {
      const colorClass = i % 2 === 0 ? "sector-even" : "sector-odd";
      sectors.push(
        <div key={i} className={`${colorClass}`} 
            style={{ transform: `rotate(${i * 45 + 22.5}deg)` }}
            onClick={() => handleSectorClick(i)}
            >
          <FontAwesomeIcon icon={faArrowUp} color="white" style={{ 
            position: 'absolute', 
            top: '50%', 
            left: '15%', 
            transform: `translate(-50%, -215%) rotate(${-67.5}deg)`, 
            filter: 'drop-shadow(0.8px 0.8px 0.8px rgba(59, 59, 59, 0.6))', 
            userSelect: 'none' // 禁止选中
          }}/>
        </div>
      );
    }
  
    return (
      <div className="circle">
        {sectors}
      </div>
    );
};


const ControlPanel: React.FC = () => {
    // 添加您的控制逻辑函数
    const handleDirection = (direction: string) => {
        console.log(`Moving: ${direction}`);
    };

    return (
        <div className="w-[260px] flex flex-col items-center justify-center p-4 bg-white rounded-lg shadow-lg">
            <h2 className="text-2xl font-semibold mb-4">云台控制</h2>
            <div className="relative">
                <Circle />
            </div>
            
            <div className="flex justify-between w-[130px] mt-4">
                <button onClick={() => handleDirection('zoom_in')} className="btn btn-sm w-[60px] text-black">
                    <FontAwesomeIcon icon={faSearchPlus} />
                </button>
                <button onClick={() => handleDirection('zoom_out')} className="btn btn-sm w-[60px] text-black">
                    <FontAwesomeIcon icon={faSearchMinus} />
                </button>
            </div>
            <div className="flex justify-between w-[130px] mt-4">
                <button onClick={() => handleDirection('left')} className="btn btn-sm w-[60px] text-black">打开</button>
                <button onClick={() => handleDirection('right')} className="btn btn-sm w-[60px] text-black">关闭</button>
            </div>
            <div className="flex justify-between w-[130px] mt-4">
                <button onClick={() => handleDirection('left')} className="btn btn-sm w-[60px] text-black">语音</button>
                <button onClick={() => handleDirection('right')} className="btn btn-sm w-[60px] text-black">截图</button>
            </div>
        </div>
    );
};

export default ControlPanel;