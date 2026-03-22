import { ReactComponent as Logo } from '../../assets/Logo.svg';
import './Header.css';
import '../style.css';

function Header() {
  return (
    // Added the 'header-container' class here
    <header className="header-container">
      <Logo id="logo"/>
      <p>The Online Exoplanet Database</p>
    </header>
  );
}

export default Header;