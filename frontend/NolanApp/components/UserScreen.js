import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
} from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import axios from "axios";

const UserScreen = () => {
  const [address, setAddress] = useState("");
  const [price, setPrice] = useState(null);
  const [waitTime, setWaitTime] = useState(null);
  const [token, setToken] = useState(null);

  useEffect(() => {
    const getToken = async () => {
      try {
        const storedToken = await AsyncStorage.getItem("jwtToken");
        if (storedToken !== null) {
          setToken(storedToken);
        }
      } catch (error) {
        // Handle error, e.g., show an error message
      }
    };
    getToken();
  }, []);

  const handleGetPrice = async () => {
    if (!token) return;
    try {
      const response = await axios.post(
        "http://10.19.11.193:5001/user/request/price",
        {
          address: address,
        },
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.status === 200) {
        const data = response.data;
        setPrice(data.requests.price);
        setWaitTime(data.requests.wait_time);
      } else {
        console.log(response);
        // Handle error, e.g., show an error message
      }
    } catch (error) {
      // Handle error, e.g., show an error message
      console.log(error);
    }
  };

  const handleSubmitRequest = async () => {
    if (!token) return;
    try {
      const response = await axios.post(
        "http://10.19.11.193:5001/user/request",
        {
          address: address,
        },
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.status === 200) {
        // Handle success, e.g., show a success message
      } else {
        // Handle error, e.g., show an error message
      }
    } catch (error) {
      console.log(error);
      // Handle error, e.g., show an error message
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Request a Line Skipper</Text>
      <TextInput
        style={styles.input}
        placeholder="Enter address"
        onChangeText={(text) => setAddress(text)}
        value={address}
      />
      <TouchableOpacity onPress={handleGetPrice} style={styles.button}>
        <Text style={styles.buttonText}>Get Price</Text>
      </TouchableOpacity>
      {price !== null && waitTime !== null && (
        <View>
          <Text style={styles.infoText}>Price: ${price.toFixed(2)}</Text>
          <Text style={styles.infoText}>
            Estimated Wait Time: {waitTime.toFixed(2)} minutes
          </Text>
          <TouchableOpacity onPress={handleSubmitRequest} style={styles.button}>
            <Text style={styles.buttonText}>Submit Request</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    paddingHorizontal: 20,
  },
  title: {
    fontSize: 24,
    marginBottom: 20,
  },
  input: {
    height: 40,
    borderColor: "gray",
    borderWidth: 1,
    paddingHorizontal: 10,
    marginBottom: 10,
  },
  button: {
    backgroundColor: "#1e90ff",
    padding: 10,
    borderRadius: 5,
    marginBottom: 10,
  },
  buttonText: {
    color: "white",
    textAlign: "center",
  },
  infoText: {
    fontSize: 18,
    marginBottom: 10,
  },
});

export default UserScreen;
