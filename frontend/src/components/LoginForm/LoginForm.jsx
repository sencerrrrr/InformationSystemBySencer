import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authAPI } from "../../api/authAPI";

export const LoginForm = () => {
  const { login } = authAPI;
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      await login(username, password);
      setError("");
      navigate("/");
    } catch (error) {
      setError(error.error || error.message || "Ошибка при входе");
    }
  };

  return (
    <div>
      <form onSubmit={handleLogin}>
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Логин"
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Пароль"
        />
        <button type="submit">Войти</button>
        {error && <p style={{ color: "red" }}>{error}</p>}
      </form>
    </div>
  );
};
