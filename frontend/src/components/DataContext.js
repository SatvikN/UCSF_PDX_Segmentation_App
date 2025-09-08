import React, { createContext, useState } from 'react';

const DataContext = createContext();

const DataContextProvider = ({ children }) => {
  const [dataState, setDataState] = useState({ selected_files: [] });

  return (
    <DataContext.Provider value={{ dataState, setDataState }}>
      {children}
    </DataContext.Provider>
  );
};

export { DataContext, DataContextProvider };


