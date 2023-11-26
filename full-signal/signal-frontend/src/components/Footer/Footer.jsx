import React from 'react'
import style from './Footer.module.scss'

export const Footer = () => {
  return (
	<div className={style.container}>
		<p>Имя пользователя: <span>Admin</span></p>
		<p class={style.center}>ООО "Рубикон"</p>
		<p>Текущая лицензия: <span>00000000</span></p>
	</div>
  )
}