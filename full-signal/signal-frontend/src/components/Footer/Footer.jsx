import React from 'react'
import style from './Footer.module.scss'

export const Footer = () => {
  return (
	<div className={style.container}>
		<p>Имя пользователя: <span>Admin</span></p>
		<p>ООО "Рубикон"</p>
		<p>Серийный номер: <span>11111111</span></p>
	</div>
  )
}