import { useContext } from 'react';
import style from './StatusBar.module.scss'
import { ChangeContext } from '../../App';
import axios from 'axios';

export const StatusBar = () => {
	const { changeStatus, setChangeStatus } = useContext(ChangeContext);

	const handleClickStatus = index => {
    	const newChangeStatus = changeStatus.map((item, i) => {
      		return i === index ? { display: 'block' } : {display: 'none'};
    	});
    	setChangeStatus(newChangeStatus);
  	};

	const downloadReport = () => {
		handleClickStatus(0);
   		axios({
      		url: 'http://127.0.0.1:8000/report/pdf',
      		method: 'GET',
      		responseType: 'blob', // important
    	}).then((response) => {
      		const url = window.URL.createObjectURL(new Blob([response.data]));
      		const link = document.createElement('a');
      		link.href = url;
      		link.setAttribute('download', 'report.pdf');
      		document.body.appendChild(link);
      		link.click();
			handleClickStatus(-1);
    	}).catch((error) => {
  			console.error(error);
		});
		
  	};

  return (
	<div className={style.container}>
		<h3>Статус и информация</h3>
		<div className={style.turnOnOff} style={{ display: changeStatus[0].display }}>
			<div></div>
			<p>Обработка...</p>
		</div>
		<div className={style.save} style={{ display: changeStatus[1].display }}>
			<a onClick={downloadReport}>PDF</a>
			<a href="!" download>Excel</a>
		</div>
		<div className={style.send} style={{ display: changeStatus[2].display }}>
			<form action="">
				<label htmlFor="email-sending">Введите email-адрес:</label>
				<input type="email" name="email-sending" id="email-sending" placeholder="example@email.com"/>
				<button>Отправить</button>
			</form>
		</div>
		<div className={style.settings} style={{ display: changeStatus[3].display }}>
			<p>P.S. Здесь будут настройки :)</p>
		</div>
	</div>
  )
}
