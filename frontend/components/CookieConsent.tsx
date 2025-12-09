'use client';

import { useEffect, useState } from 'react';

export default function CookieConsent() {
  const [isVisible, setIsVisible] = useState(false);
  const [isChecked, setIsChecked] = useState(false);

  useEffect(() => {
    const consent = localStorage.getItem('cookieConsent');
    if (consent !== 'accepted') {
      setIsVisible(true);
    }
  }, []);

  const handleAccept = () => {
    if (isChecked) {
      localStorage.setItem('cookieConsent', 'accepted');
      setIsVisible(false);
    }
  };

  if (!isVisible) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-gray-800 text-white p-4 z-50">
      <div className="container mx-auto flex flex-col md:flex-row items-center justify-between">
        <p className="mb-4 md:mb-0">
          Pour certaines fonctionnalités, vous serez redirigé vers des sites tiers. 
          Aucune donnée de connexion ne sera conservée.
        </p>
        <div className="flex items-center">
          <label className="flex items-center mr-4">
            <input 
              type="checkbox" 
              className="form-checkbox h-5 w-5 text-blue-600 mr-2"
              checked={isChecked}
              onChange={(e) => setIsChecked(e.target.checked)}
            />
            <span>J'ai compris</span>
          </label>
          <button
            onClick={handleAccept}
            className={`py-2 px-4 rounded font-medium ${
              isChecked 
                ? 'bg-blue-600 hover:bg-blue-700 text-white' 
                : 'bg-gray-400 text-gray-600 cursor-not-allowed'
            }`}
            disabled={!isChecked}
          >
            Continuer
          </button>
        </div>
      </div>
    </div>
  );
}
