import Header from './Header';
import SideBar from './SideBar';
// DataContextProvider moved to App-level so state persists across routes
import '../styles/index.css';

const Layout = (Component) => ({ ...props }) => (
    <div className="layout">
      <div className="header" >
        <Header />
      </div>
      
      <div className="container1">
        <div className="">
          <SideBar />
        </div>
        
        <div className="main-container">
          <Component {...props} />
        </div>
      </div>
    </div>
);

export default Layout;


