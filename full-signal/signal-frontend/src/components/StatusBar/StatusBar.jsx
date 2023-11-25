import { useContext } from 'react';
import style from './StatusBar.module.scss'
import { ChangeStatusContext } from '../../App';

export const StatusBar = () => {
	const { changeStatus } = useContext(ChangeStatusContext);

  return (
	<div className={style.container}>
		<h3>Статус и информация</h3>
		<div className={style.turnOnOff} style={{ display: changeStatus[0].display }}>
			<div></div>
			<p>Обработка...</p>
		</div>
		<div className={style.save} style={{ display: changeStatus[1].display }}>
			<a href="!" download>PDF</a>
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
