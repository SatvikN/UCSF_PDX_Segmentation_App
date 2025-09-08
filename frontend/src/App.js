import React from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import './styles/index.css';
import Layout from './layouts/Layout';
import Home from './routes/index';
import Models from './routes/Option1';
import Calculations from './routes/Option2';
import Images from './routes/Option3';
import Saving from './routes/Option4';
import { DataContextProvider } from './components/DataContext';

const HomeComponent = Layout(Home);
const Option1Component = Layout(Models);
const Option2Component = Layout(Calculations);
const Option3Component = Layout(Images);
const Option4Component = Layout(Saving);

const router = createBrowserRouter([
  { path: '/', element: <HomeComponent /> },
  { path: '/model', element: <Option1Component /> },
  { path: '/information', element: <Option2Component /> },
  { path: '/images', element: <Option3Component /> },
  { path: '/saving', element: <Option4Component /> },
]);

export default function App() {
  return (
    <div className="App">
      <DataContextProvider>
        <RouterProvider router={router} />
      </DataContextProvider>
    </div>
  );
}


