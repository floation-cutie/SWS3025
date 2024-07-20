import React, { useState, useEffect } from 'react';
import * as echarts from 'echarts';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCloud, faDroplet, faSun, faTemperatureHigh, faWind } from '@fortawesome/free-solid-svg-icons';

const DataInfo: React.FC = () => {
    const [currentWeather, setCurrentWeather] = useState({
        cityname: '', temp: '', humidity: '', windspeed: '', description: ''
    });
    const [forecast, setForecast] = useState([]);

    useEffect(() => {
        // 获取当前位置
        const fetchLocationAndWeather = async () => {
            try {
                const locationResponse = await fetch('http://192.168.92.51:8008/location');
                // 1.295164, 103.775055
                let latitude = 1.294619;
                let longitude = 103.774965;
                const locationData = await locationResponse.json();
                if (locationResponse.ok && locationData.status !== 'error') {
                    latitude = locationData.latitude;
                    longitude = locationData.longitude;
                }
                const apiKey = 'YOUR_API_KEY';
                const weatherUrl = `https://api.openweathermap.org/data/2.5/weather?lat=${latitude}&lon=${longitude}&appid=${apiKey}&units=metric`;
                const forecastUrl = `https://api.openweathermap.org/data/2.5/forecast?lat=${latitude}&lon=${longitude}&appid=${apiKey}&units=metric`;

                // 获取当前天气
                const weatherResponse = await fetch(weatherUrl);
                const weatherData = await weatherResponse.json();
                if (weatherResponse.ok) {
                    setCurrentWeather({
                        cityname: weatherData.name,
                        temp: `${weatherData.main.temp} °C`,
                        humidity: `${weatherData.main.humidity} %`,
                        windspeed: `${weatherData.wind.speed} m/s`,
                        description: weatherData.weather[0].description
                    });
                }

                // 获取天气预报
                const forecastResponse = await fetch(forecastUrl);
                const forecastData = await forecastResponse.json();
                if (forecastResponse.ok) {
                    setForecast(forecastData.list.map(item => ({
                        time: new Date(item.dt * 1000).toLocaleString(),
                        temp: item.main.temp,
                        description: item.weather[0].description
                    })));
                }
            } catch (error) {
                console.error('Fetch error:', error);
            }
        };

        fetchLocationAndWeather();
    }, []);

    useEffect(() => {
        const chartDom = document.getElementById('forecastChart');
        if (forecast.length > 0 && chartDom) {
            const myChart = echarts.init(chartDom);
            myChart.setOption({
                // title:
                title: null,
                grid: {
                  top: 20, // 上边距减少
                  right: 20, // 右边距减少
                  bottom: 30, // 下边距减少
                  left: 40 // 左边距保持
                },
                tooltip: {
                    trigger: 'axis',
                    formatter: function (params) {
                        const param = params[0];
                        return `${param.axisValueLabel}<br/>Temperature: ${param.data.value}°C<br/>Weather: ${param.data.description}`;
                    }
                },
                xAxis: {
                    type: 'category',
                    data: forecast.map(item => item.time),
                    axisLabel: {
                      formatter: function (value) {
                          // Assuming the value format is "YYYY/MM/DD HH:mm:ss"
                          // Convert it to "M/D HH:mm"
                          const date = new Date(value);
                          return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:00`;
                      }
                  }
                },
                yAxis: {
                    type: 'value',
                    axisLabel: {
                        formatter: '{value} °C'
                    }
                },
                series: [{
                    data: forecast.map(item => ({ value: item.temp, description: item.description })),
                    type: 'line',
                    smooth: true
                }]
            });

            return () => {
                myChart.dispose(); // Clean up the chart if the component unmounts
            };
        }
    }, [forecast]);

    return (
        <div className="w-[550px] bg-white shadow-lg rounded-lg p-5">
            <h2 className="text-xl font-semibold mb-4">
              Weather Info - {currentWeather.cityname}
            </h2>
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-2">Current Weather</h3>
              <div className="flex items-center mb-2">
                  <div className="w-5 flex justify-center"><FontAwesomeIcon icon={faTemperatureHigh} /></div>
                  <p className="ml-1"><b>Temperature:</b> {currentWeather.temp}</p>
              </div>
              <div className="flex items-center mb-2">
                  <div className="w-5 flex justify-center"><FontAwesomeIcon icon={faDroplet} /></div>
                  <p className="ml-1"><b>Humidity:</b> {currentWeather.humidity}</p>
              </div>
              <div className="flex items-center mb-2">
                  <div className="w-5 flex justify-center"><FontAwesomeIcon icon={faWind} /></div>
                  <p className="ml-1"><b>Wind Speed:</b> {currentWeather.windspeed}</p>
              </div>
              <div className="flex items-center mb-2">
                  <div className="w-5 flex justify-center"><FontAwesomeIcon icon={faCloud} /></div>
                  <p className="ml-1"><b>Weather:</b> {currentWeather.description}</p>
              </div>
          </div>
            <div>
                <h3 className="text-lg font-semibold mb-2">Five-day Weather Forecast</h3>
                <div className="mx-auto" id="forecastChart" style={{ width: '380px', height: '320px' }}></div>
            </div>
        </div>
    );
};

export default DataInfo;
