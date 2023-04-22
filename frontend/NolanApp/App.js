import React, { useState } from "react";
import {
  SafeAreaView,
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
} from "react-native";
import LoginForm from "./components/LoginForm";
import UserScreen from "./components/UserScreen";
import LineSitterScreen from "./components/LineSitterScreen";
import RegisterScreen from "./components/RegisterScreen";

const App = () => {
  const [user, setUser] = useState(null);
  const [screen, setScreen] = useState("login");

  const handleLogin = (userData) => {
    setUser(userData);
    setScreen("user");
  };

  const handleLogout = () => {
    setUser(null);
    setScreen("login");
  };

  const handleRegister = () => {
    setScreen("register");
  };

  const handleBackToLogin = () => {
    setScreen("login");
  };

  const handleLineSitterLogin = (userData) => {
    setUser(userData);
    setScreen("lineSitter")
  }

  const renderScreen = () => {
    switch (screen) {
      case "login":
        return (
          <LoginForm
            onLogin={handleLogin}
            onRegister={handleRegister}
            onLoginAsLineSitter={handleLineSitterLogin}
          />
        );
      case "register":
        return <RegisterScreen onBackToLogin={handleBackToLogin} />;
      case "user":
        return <UserScreen user={user} onLogout={handleLogout} />;
      case "lineSitter":
        return <LineSitterScreen user={user} onLogout={handleLogout} />;
      default:
        return <LoginForm onLogin={handleLogin} onRegister={handleRegister} />;
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Nolan</Text>
      </View>
      {renderScreen()}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    backgroundColor: "#3a3a3a",
    padding: 20,
  },
  title: {
    color: "#fff",
    fontSize: 24,
    fontWeight: "bold",
    textAlign: "center",
  },
});

export default App;
