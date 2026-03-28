import { Layout } from './components/Layout/Layout';
import { LandingPage } from './components/Landing/LandingPage';
import { ErrorBoundary } from './components/common/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <Layout>
        <LandingPage />
      </Layout>
    </ErrorBoundary>
  );
}

export default App;
