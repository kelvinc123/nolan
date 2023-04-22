import React, { useState, useEffect } from "react";
import { View, Text, StyleSheet } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import axios from "axios";

const LineSitterScreen = () => {
  const [requestData, setRequestData] = useState(null);

  useEffect(() => {
    const fetchRequestData = async () => {
      try {
        const token = await AsyncStorage.getItem("jwtToken");
        if (token !== null) {
          const response = await axios.get(
            "http://10.19.11.193:5001/line_sitter/request",
            {
              headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
              },
            }
          );
          if (response.status === 200) {
            const data = response.data;
            setRequestData(data.result);
          } else {
            console.log("status not 200!")
            // Handle error, e.g., show an error message
          }
        }
      } catch (error) {
        console.log(error);
        // Handle error, e.g., show an error message
      }
    };
    (async () => {
        await fetchRequestData();
      })();
    }, []);
  
    return (
      <View style={styles.container}>
        {requestData && (
          <View>
            <Text style={styles.title}>Ongoing Request</Text>
            <Text style={styles.infoText}>
              Formatted Address: {requestData.formatted_address}
            </Text>
            <Text style={styles.infoText}>Address: {requestData.address}</Text>
            <Text style={styles.infoText}>Zip Code: {requestData.zip_code}</Text>
            <Text style={styles.infoText}>
              Price: ${requestData.price.toFixed(2)}
            </Text>
            <Text style={styles.infoText}>
              Time to Destination: {Math.round(requestData.time_to_destination)}{" "}
              minutes
            </Text>
            <Text style={styles.infoText}>
              Estimated Wait Time: {requestData.estimated_wait_time} minutes
            </Text>
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
  infoText: {
    fontSize: 18,
    marginBottom: 10,
  },
});

export default LineSitterScreen;
