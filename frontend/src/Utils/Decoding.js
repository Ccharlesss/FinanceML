// import base64 from "base-64";

// // Purpose: Encode a string using Base64
// export const str_encode = (string) => {
//   return base64.encode(string);
// };

// // Purpose: Decode a Base64 encoded string
// export const str_decode = (string) => {
//   return base64.decode(string);
// };

// // Example encoding function (make sure it matches what you did in the backend)
// export const str_encode = (string) => {
//   return btoa(string); // Use btoa to encode to Base64
// };

// // Example decoding function
// export const str_decode = (string) => {
//   return atob(string); // Use atob to decode from Base64
// };

// ==================================================================================================

// Importing the base64 utility
// import base64 from "base-64"; // Make sure to have this import if you use the base-64 library

// // Purpose: Encode a string using Base64
// export const str_encode = (string) => {
//   return base64.encode(string);
// };

// // Purpose: Decode a Base64 encoded string
// export const str_decode = (string) => {
//   // Convert URL-safe Base64 to standard Base64
//   let base64String = string.replace(/-/g, "+").replace(/_/g, "/");

//   // Pad the Base64 string with `=` to make it a multiple of 4
//   const padding = base64String.length % 4;
//   if (padding) {
//     base64String += "=".repeat(4 - padding);
//   }

//   return base64.decode(base64String); // Use the base64.decode function
// };
// ==================================================================================================
// import { decode } from "base-64";

// // Purpose: Decode a Base64 encoded string
// export const str_decode = (string) => {
//   try {
//     return decode(string); // Decode the Base64 string
//   } catch (error) {
//     console.error("Error decoding Base64 string:", error);
//     return null; // Handle errors gracefully
//   }
// };
