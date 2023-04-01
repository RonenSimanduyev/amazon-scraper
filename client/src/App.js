import './App.css';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { routes } from './routes';
import { HomePage } from './views/HomePage';


function App() {
  return (
    <BrowserRouter>

      <Routes>

        <Route path={routes.home} element={<HomePage />} />

      </Routes>

    </BrowserRouter>


  )
}

export default App;
