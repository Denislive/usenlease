// db.js
const dbName = 'FormDataDB';
const storeName = 'formDataStore';

let db;

// Function to open the IndexedDB
const openDB = () => {
  return new Promise((resolve, reject) => {
    console.log('Opening database:', dbName);
    const request = indexedDB.open(dbName, 2); // Increment the version number if you change the structure

    request.onupgradeneeded = (event) => {
      console.log('Database upgrade needed:', event);
      db = event.target.result;
      // Create the object store if it doesn't exist
      if (!db.objectStoreNames.contains(storeName)) {
        db.createObjectStore(storeName, { keyPath: 'id', autoIncrement: true });
        console.log(`Object store '${storeName}' created.`);
      }
    };

    request.onsuccess = (event) => {
      db = event.target.result;
      console.log('Database opened successfully:', db);
      resolve(db);
    };

    request.onerror = (event) => {
      console.error('Database error:', event.target.errorCode);
      reject('Database error: ' + event.target.errorCode);
    };
  });
};

// Function to save form data to IndexedDB
const saveFormData = (data) => {
    return new Promise((resolve, reject) => {
      const transaction = db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.add(data);
  
      request.onsuccess = () => {
        resolve();
      };
  
      request.onerror = (event) => {
        reject('Error saving data: ' + event.target.errorCode);
      };
    });
  };

// Function to load all form data from IndexedDB
const loadFormData = async () => {
  await openDB(); // Ensure the database is open
  return new Promise((resolve, reject) => {
    console.log('Loading form data from IndexedDB...');
    const transaction = db.transaction([storeName], 'readonly');
    const store = transaction.objectStore(storeName);
    const request = store.getAll(); // Get all records

    request.onsuccess = (event) => {
      const loadedData = event.target.result;
      console.log('Data loaded successfully:', loadedData);
      
      // Ensure that the data is in the same state as when it was stored
      const processedData = loadedData.map(item => {
        // If there are base64 images, ensure they are in the correct format
        if (item.images && item.images.base64) {
          item.images.base64 = item.images.base64; // Ensure it's still a valid base64 string
        }
        return item;
      });

      resolve(processedData);
    };

    request.onerror = (event) => {
      console.error('Error loading data:', event.target.errorCode);
      reject('Error loading data: ' + event.target.errorCode);
    };
  });
};

// Function to clear all data from the object store
const clearFormData = async () => {
  await openDB(); // Ensure the database is open
  return new Promise((resolve, reject) => {
    console.log('Clearing all data from object store:', storeName);
    const transaction = db.transaction([storeName], 'readwrite');
    const store = transaction.objectStore(storeName);
    const request = store.clear(); // Clear all records

    request.onsuccess = () => {
      console.log('All data cleared successfully.');
      resolve();
    };

    request.onerror = (event) => {
      console.error('Error clearing data:', event.target.errorCode);
      reject('Error clearing data: ' + event.target.errorCode);
    };
  });
};

export { openDB, saveFormData, loadFormData, clearFormData };