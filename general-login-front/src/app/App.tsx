import { AppRouter } from "./providers/router";
import { MainLayout } from "./layouts/MainLayout";

function App() {
  return (
    <MainLayout>
      <AppRouter />
    </MainLayout>
  );
}

export default App;
