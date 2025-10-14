import ChatWidget from './components/ChatWidget';

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            🏡 DreamHome Realty
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Find Your Perfect Home with AI-Powered Assistance
          </p>
          <div className="flex gap-4 justify-center">
            <button className="bg-purple-600 text-white px-8 py-3 rounded-lg hover:bg-purple-700 transition">
              Browse Properties
            </button>
            <button className="border-2 border-purple-600 text-purple-600 px-8 py-3 rounded-lg hover:bg-purple-50 transition">
              Learn More
            </button>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white p-8 rounded-xl shadow-lg">
            <div className="text-4xl mb-4">🏠</div>
            <h3 className="text-xl font-semibold mb-2">Premium Properties</h3>
            <p className="text-gray-600">
              Curated selection of luxury homes and apartments
            </p>
          </div>
          <div className="bg-white p-8 rounded-xl shadow-lg">
            <div className="text-4xl mb-4">💰</div>
            <h3 className="text-xl font-semibold mb-2">Best Prices</h3>
            <p className="text-gray-600">
              Competitive pricing with transparent deals
            </p>
          </div>
          <div className="bg-white p-8 rounded-xl shadow-lg">
            <div className="text-4xl mb-4">🤝</div>
            <h3 className="text-xl font-semibold mb-2">Expert Guidance</h3>
            <p className="text-gray-600">
              24/7 AI-powered support for all your queries
            </p>
          </div>
        </div>

        <div className="bg-gradient-to-r from-purple-600 to-purple-800 text-white p-12 rounded-2xl text-center">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Find Your Dream Home?
          </h2>
          <p className="text-lg mb-6">
            Chat with Maya, our AI assistant, to get started!
          </p>
          <p className="text-purple-200">
            👉 Click the chat button in the bottom-right corner
          </p>
        </div>
      </div>

      <ChatWidget />
    </div>
  );
}

export default App;