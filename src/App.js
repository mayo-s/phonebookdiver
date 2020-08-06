import React from 'react';
import { BrowserRouter, Switch, Route } from 'react-router-dom';
import Navbar from './components/layout/Navbar';
import Dashboard from './components/dashboard/Dashboard';
import Map from './components/heatmap/Map';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Navbar />
        <Switch>
          <Route exact path='/' component={Dashboard} />
          <Route path='/heatmap' component={Map} />
          {/* <Route path='/imprint' component={Imprint} /> */}
        </Switch>
      </div>
    </BrowserRouter>
  );
}

export default App