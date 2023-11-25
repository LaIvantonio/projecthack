import React, { useContext, useEffect, useState } from 'react'
import style from './Header.module.scss'
import { ChangeStatusContext } from '../../App';
import axios from 'axios';

export const Header = () => {
	const [networkInfo, setNetworkInfo] = useState(null);
	const [greeting, setGreeting] = useState("");
	const [dateTime, setDateTime] = useState(new Date().toLocaleString());

	useEffect(() => {
		const date = new Date();
		const hours = date.getHours();

		if (hours < 12) {
     		setGreeting('Доброе утро,');
   		} else if (hours < 18) {
    		setGreeting('Добрый день,');
   		} else if (hours < 24) {
     		setGreeting('Добрый вечер,');
   		} else {
     		setGreeting('Доброй ночи,');
   		}
	}, []);

	useEffect(() => {
   		const timer = setInterval(() => {
     		setDateTime(new Date().toLocaleString());
   		}, 1000);

   		return () => {
     		clearInterval(timer);
   		};
 	}, []);

	const { changeStatus, setChangeStatus } = useContext(ChangeStatusContext);

	const handleClickStatus = index => {
    	const newChangeStatus = changeStatus.map((item, i) => {
      		return i === index ? { display: 'block' } : {display: 'none'};
    	});
    	setChangeStatus(newChangeStatus);
  	};

	const getInfo = () => {
		axios.get('/api/devices').then(response => {
			if (response.status === 200) {
				setNetworkInfo(response.data);
				console.log(networkInfo);
			} else {
				console.log(`Упс! Что-то пошло не так. Статус запроса: ${response.status}`);
			}
		})
	}

  return (
	<div className={style.header}>
		<div className={style.leftBar}>
			<svg width="90px" height="90px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
				<g id="SVGRepo_bgCarrier" stroke-width="0"/>
				<g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"/>
				<g id="SVGRepo_iconCarrier"> <path opacity="0.4" d="M9.41977 2.15994L3.91977 4.21994C2.86977 4.60994 2.00977 5.85993 2.00977 6.97993V15.0799C2.00977 15.8899 2.53977 16.9599 3.18977 17.4399L8.68977 21.5499C9.65977 22.2799 11.2498 22.2799 12.2198 21.5499L17.7198 17.4399C18.3698 16.9499 18.8998 15.8899 18.8998 15.0799V6.97993C18.8998 5.85993 18.0398 4.60994 16.9898 4.21994L11.4898 2.15994C10.9198 1.94994 9.98977 1.94994 9.41977 2.15994Z" fill="#457b9d"/> <path d="M19.2601 6.75977H12.4102C12.2102 6.75977 12.0201 6.76978 11.8401 6.76978C10.1201 6.86978 9.66016 7.49978 9.66016 9.45978V9.84978C9.66016 10.264 9.99594 10.5998 10.4102 10.5998H21.2502C21.6644 10.5998 22.0002 10.264 22.0002 9.84978V9.45978C22.0002 7.29978 21.4501 6.75977 19.2601 6.75977Z" fill="#457b9d"/> <path d="M10.4199 11.7002C10.0057 11.7002 9.66992 12.036 9.66992 12.4502V14.5402C9.66992 16.7002 10.2199 17.2502 12.4099 17.2502H19.2599C21.4099 17.2502 21.9799 16.7302 21.9999 14.6602V12.4502C21.9999 12.036 21.6641 11.7002 21.2499 11.7002H10.4199ZM13.2699 15.4702H12.0199C11.7199 15.4702 11.4799 15.2302 11.4799 14.9302C11.4799 14.6302 11.7199 14.3902 12.0199 14.3902H13.2699C13.5699 14.3902 13.8099 14.6302 13.8099 14.9302C13.8099 15.2302 13.5699 15.4702 13.2699 15.4702ZM17.3199 15.4702H14.8299C14.5299 15.4702 14.2899 15.2302 14.2899 14.9302C14.2899 14.6302 14.5299 14.3902 14.8299 14.3902H17.3199C17.6199 14.3902 17.8599 14.6302 17.8599 14.9302C17.8699 15.2302 17.6199 15.4702 17.3199 15.4702Z" fill="#457b9d"/> </g>
			</svg>
			<h1>{greeting}<br/> <span>администратор!</span></h1>
		</div>
		<div className={style.buttonContainer}>
			<button
				onClick={() => {
					handleClickStatus(0);
				}}
			><img src="turn-onoff.svg" alt='turn on/off'/>Запустить</button>
			<button
				onClick={() => {handleClickStatus(1)}}
			><img src="save.svg" alt='save'/>Сохранить</button>
			<button
				onClick={() => {handleClickStatus(2)}}
			><img src="repost.svg" alt='send'/>Отправить</button>
			<button
				onClick={() => {handleClickStatus(3)}}
			><img src="settings.svg" alt='settings'/>Параметры</button>
		</div>
		<div className={style.rightBar}>
			<p className={style.paragraph}>Текущее время и дата:</p>
			<p className={style.dateAndTime}>{dateTime}</p>
		</div>
	</div>
  )
}
