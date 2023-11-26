import React, { useContext, useState } from 'react'
import style from './Info.module.scss'
import { ChangeContext } from '../../App';

export const Info = () => {
	const [radioValue, setRadioValue] = useState("Операционная система");

	const {networkInfo} = useContext(ChangeContext);

	const getInfo = () => {
		let outputInfo = [];
		if (radioValue === "Операционная система") {
			for (const property in networkInfo[0]) {
				if (networkInfo[0][property] !== undefined) {
					outputInfo.push(<p><span>{property}</span>{`: ${networkInfo[0][property]}`}</p>);
				}
			}
		} else if (radioValue === "Устройства") {
			networkInfo[1].forEach(device => {
				for (const property in device) {
					if (device[property] !== undefined && property !== "Name") {
						outputInfo.push(<p><span>{property}</span>{`: ${device[property]}`}</p>);
					} else if (device[property] !== undefined && property === "Name")  {
						outputInfo.push(<h3>{`${property}: ${device[property]}`}</h3>);
					}
					if (property === "Type") {
						outputInfo.push(<br></br>);
					}
				}
			});
		} else if (radioValue === "Установленное ПО") {
			networkInfo[2].forEach(device => {
				for (const property in device) {
					if (device[property] !== undefined) {
						outputInfo.push(<p><span>{property}</span>{`: ${device[property]}`}</p>);
					}

					if (property === "version") {
						outputInfo.push(<br></br>);
					}
				}
			});
		}

		return outputInfo;
	}

  return (
	<div className={style.container}>
		<h4>
			{
				networkInfo !== null ? 
				<>Серийный номер<span>{networkInfo[3].bios_serial}</span></> : 
				"Окно отчёта"
			}
		</h4>
		<div className={style.parameters}>
			{
				networkInfo !== null ? 
				<>
					{
						["Операционная система", "Устройства", "Установленное ПО"].map((option) => (
							<div key={option}>
								<input 
									type='radio'
									name='parameters'
									value={option}
									checked={option === radioValue}
									onChange={() => setRadioValue(option)}
								/>
								<label htmlFor={option}>{option}</label>
							</div>
						))
					}
				</>
				: null
			}
		</div>
		<div className={style.reportContainer}>
			{networkInfo !== null ? getInfo() : <p>Здесь будет отображаться Ваш <span>отчёт</span></p>}
		</div>
	</div>
  )
}
