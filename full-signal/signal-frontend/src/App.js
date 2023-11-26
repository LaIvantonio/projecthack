import { Footer } from './components/Footer/Footer';
import {Header} from './components/Header/Header';
import { Info } from './components/Info/Info';
import { StatusBar } from './components/StatusBar/StatusBar';
import React, { useState } from 'react';

export const ChangeContext = React.createContext();

function App() {

  const [changeStatus, setChangeStatus] = useState([
    { display: 'none' },
    { display: 'none' },
    { display: 'none' },
    { display: 'none' }
  ]);

  const [networkInfo, setNetworkInfo] = useState(null);
  
  return (
    <ChangeContext.Provider value={{ 
        changeStatus, 
        setChangeStatus, 
        networkInfo,
        setNetworkInfo
      }}>
      <div className="App" style={{padding: "1rem 2rem"}}>
      <Header/>
        <div style={{display: "flex", justifyContent: "space-between", alignContent: "center"}}>
          <StatusBar/>
          <Info/>
        </div>
      </div>
      <Footer/>
    </ChangeContext.Provider>  
  );
}

export default App;
