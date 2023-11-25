import { Footer } from './components/Footer/Footer';
import {Header} from './components/Header/Header';
import { Info } from './components/Info/Info';
import { StatusBar } from './components/StatusBar/StatusBar';
import React, { useState } from 'react';

export const ChangeStatusContext = React.createContext();

function App() {

  const [changeStatus, setChangeStatus] = useState([
    { display: 'none' },
    { display: 'none' },
    { display: 'none' },
    { display: 'none' }
  ]);
  
  return (
    <ChangeStatusContext.Provider value={{ changeStatus, setChangeStatus }}>
      <div className="App" style={{padding: "1rem 2rem"}}>
      <Header/>
        <div style={{display: "flex", justifyContent: "space-between", alignContent: "center"}}>
          <StatusBar/>
          <Info/>
        </div>
      </div>
      <Footer/>
    </ChangeStatusContext.Provider>  
  );
}

export default App;
