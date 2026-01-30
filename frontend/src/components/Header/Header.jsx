import { Link, useNavigate } from "react-router-dom";
import { useContext } from "react";
import { AuthContext } from "../../contexts/AuthContext"

export const Header = () => {
  const { isAuthenticated, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      navigate("/login", { replace: true });
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

          {!isAuthenticated ? (
            <li>
              <Link to="/login">Войти</Link>
            </li>
          ) : (
            <li>
              <button type="button" onClick={handleLogout}>
                Выйти
              </button>
            </li>
          )}
        </ul>
      </nav>
    </header>
  );
};
