import { Link } from "react-router-dom";
import { authAPI } from "../../api/authAPI";

export const Header = () => {
  const { logout } = authAPI;

  const handleLogout = async () => {
    try {
      await logout();
    } catch (e) {
      console.error("Ошибка выхода", e);
    }
  };

  return (
    <header>
      <nav>
        <ul>
          <li>
            <Link to="/">Главная</Link>
          </li>

          <li>
            <Link to="/login">Вход</Link>
          </li>

          <li>
            <button type="button" onClick={handleLogout}>
              Выйти
            </button>
          </li>
        </ul>
      </nav>
    </header>
  );
};
